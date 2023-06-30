from genericpath import exists
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST)
from api.utils import getparameter
import survey
from xperthaler_backend import constants
from rest_framework.response import Response
from inhaler.models import Device, Inhalation
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, UpdateView
from survey.models import DailySurvey
import json
from django.utils.translation import ugettext_lazy as _
from .forms import *
from django.contrib import messages
from datetime import date, timedelta

# API to get inhalations data for calendar
class CalendarInhalationList(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            survey_date = getparameter(request, 'survey_date')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
            range_start = survey_date+' 00:00:00'
            range_end = survey_date+' 23:59:59'
            inhalations =  Inhalation.objects.filter(device__user = user_obj, inhalation_time__range=(range_start, range_end))
            inhalation_data = []
            for i in inhalations:
                data = {}
                data['time'] = i.inhalation_time.strftime('%H:%M')
                if i.x_angle >= 45 and i.y_angle >= 45:
                    data['angle'] = 1
                else:
                    data['angle'] = 0
                data['shaken'] = i.shaken
                inhalation_data.append(data)
            response = {'status': 200, 'data': inhalation_data}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)


# API to get data for reports
class GetReportsData(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            page = getparameter(request, 'page')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        inhalations =  Inhalation.objects.filter(user = user_obj).order_by('-inhalation_time')
        page = int(page)
        page_min = 10 * (page-1)
        page_max = 10 * page
        inhalations = inhalations[page_min:page_max]
        inhalation_data = []
        for i in inhalations:
            data = {}
            if i.device.medicine_type:
                data['type'] = 'Rescue Dose'
            else:
                data['type'] = 'Maintanence Dose'
            data['inhalation_time'] = i.inhalation_time.strftime('%H:%M')+'['+ i.inhalation_time.strftime('%d-%m-%Y')+']'
            data['recommended_time'] = ''
            data['deviation'] = ''
            if i.shaken:
                data['shaken'] = 'Okay'
            else:
                data['shaken'] = 'Not Okay'
            if i.angle:
                data['angle'] = 'Okay'
            else:
                data['angle'] = 'Not Okay'
            data['location'] = i.location
            # if SurveyRating.objects.filter(user = user_obj, date = i.inhalation_time).exists():
            #     data['rating'] = str(SurveyRating.objects.get(user = user_obj, date = i.inhalation_time).rating) + '/10'
            # else:
            #     data['rating'] = '0/10'
            inhalation_data.append(data)
        response = {'status': 200, 'reports_data': inhalation_data}
        return Response(response, status = HTTP_200_OK)

def changedashboarddosetype(request):
    if 'med_type' in request.GET:
        med_type = request.GET['med_type']
        request.session['med_type'] = med_type
    return redirect('user:dashboard')


def adddata(request):
    data = {}
    data['page_title'] = 'Add data'
    return render(request,'add_data.html', data)


class Reports(LoginRequiredMixin, TemplateView):
    template_name = "reports.html"
    def get_context_data(self, *args, **kwargs):
        context = super(Reports, self).get_context_data(*args, **kwargs)
        report_data = []
        inhalations =  Inhalation.objects.filter(device__user = self.request.user).order_by('-inhalation_time')
        data = {}
        inhalation_data = []
        for i in inhalations:
            data = {}
            if i.device.medicine_type:
                data['type'] = 'Rescue Dose'
            else:
                data['type'] = 'Maintanence Dose'
            data['inhalation_time'] = i.inhalation_time.strftime('%H:%M')+'['+ i.inhalation_time.strftime('%d-%m-%Y')+']'
            data['recommended_time'] = ''
            data['deviation'] = ''
            if i.shaken:
                data['shaken'] = 'Okay'
            else:
                data['shaken'] = 'Not Okay'
            data['x_angle'] = i.x_angle
            data['y_angle'] = i.y_angle
            data['location'] = i.location
            if DailySurvey.objects.filter(user = self.request.user, date = i.inhalation_time).exists():
                daily_survey_obj = DailySurvey.objects.get(user = self.request.user, date = i.inhalation_time)
                if daily_survey_obj.survey_rating is None:
                    survey = daily_survey_obj.survey
                    survey = json.loads(survey)
                    rating = str(survey['1']) + '/10'
                else:
                    rating = str(daily_survey_obj.survey_rating) + '/10'
            else:
                rating = '0/10'
            data['rating'] = rating
            inhalation_data.append(data)
        context['inhalation_data'] = inhalation_data
        return context

class ReportsView(LoginRequiredMixin, ListView):
    template_name = 'reports.html'
    model = Inhalation
    paginate_by = 10

    def get_queryset(self, **kwargs):
        notifications = Inhalation.objects.filter(device__user = self.request.user)
        return notifications

    def get_context_data(self, *args, **kwargs):
        context = super(ReportsView, self).get_context_data(*args, **kwargs)
        context['page_title'] = _('Reports')
        user = self.request.user
        joined_date = user.date_joined.date()
        delta = date.today() - joined_date
        report_data = []
        for i in range(delta.days + 1):
            data = {}
            report_date = joined_date + timedelta(days=i)
            data['date'] = report_date.strftime('%Y-%m-%d')
            data['count'] = Inhalation.objects.filter(device__user = user, inhalation_time__date = report_date).count()
            if DailySurvey.objects.filter(user = user, date = report_date).exists():
                rating = DailySurvey.objects.get(user = user, date = report_date).survey_rating
                if rating is None:
                    rating = 0
            else:
                rating = 0
            data['rating'] = rating
            report_data.append(data)
        print(report_data)
        context['report_data'] = report_data
        return context

class PatientReportsView(LoginRequiredMixin, ListView):
    template_name = 'reports.html'
    model = Inhalation
    paginate_by = 10

    def get_queryset(self, **kwargs):
        notifications = Inhalation.objects.filter(device__user__id = self.kwargs['pk'])
        return notifications
    
    def get_context_data(self, *args, **kwargs):
        context = super(PatientReportsView, self).get_context_data(*args, **kwargs)
        context['page_title'] = _('Patient reports')
        user = User.objects.get(id =self.kwargs['pk'])
        joined_date = user.date_joined.date()
        delta = date.today() - joined_date
        report_data = []
        for i in range(delta.days + 1):
            data = {}
            report_date = joined_date + timedelta(days=i)
            data['date'] = report_date.strftime('%Y-%m-%d')
            data['count'] = Inhalation.objects.filter(device__user = user, inhalation_time__date = report_date).count()
            if DailySurvey.objects.filter(user = user, date = report_date).exists():
                rating = DailySurvey.objects.get(user = user, date = report_date).survey_rating
                if rating is None:
                    rating = 0
            else:
                rating = 0
            data['rating'] = rating
            report_data.append(data)
        print(report_data)
        context['report_data'] = report_data
        return context

class DevicesListView(LoginRequiredMixin, ListView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'devices_list.html'
    model = Device
    paginate_by = 10

    def get_queryset(self, **kwargs):
        devices = Device.objects.filter(user = self.request.user).order_by('ble_name')
        return devices

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Devices')
        return context

class DeviceAlarmsView(LoginRequiredMixin, UpdateView):
    form_class = DeviceAlarmsForm
    template_name = "edit_device_alarms.html"
    title = _('Edit device alarms')

    def get_object(self, queryset=None):
        return DeviceAlarm.objects.get(id = self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DeviceAlarmsView, self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        context['id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Device alarms saved.'))
        return redirect('inhaler:devices')