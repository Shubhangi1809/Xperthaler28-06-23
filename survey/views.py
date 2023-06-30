from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Questions
from django.views.generic import (DeleteView, DetailView, FormView, ListView,
                                  RedirectView, TemplateView, UpdateView, View)
from rest_framework.views import APIView
from api.utils import getparameter
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)
from rest_framework.response import Response
from xperthaler_backend import constants
from .models import Questions, DailySurvey
from datetime import date, datetime
from rest_framework.permissions import AllowAny
from django.contrib.auth.mixins import LoginRequiredMixin
from xperthaler_backend.settings.configuration import WEATHER_API_KEY
from xperthaler_backend.constants import WEATHER_API_URL
import requests
import json
from django.db import transaction
from survey.models import DailySurvey
from inhaler.models import Inhalation
import json
from django.contrib import messages

# Create your views here.
class Survey(LoginRequiredMixin, TemplateView):
    template_name = "survey.html"

    def get(self, *args , **kwargs):
        context = {}
        data = []
        survey_date = self.request.GET.get('survey_date', date.today().strftime('%Y-%m-%d'))
        try:
            survey_date = datetime.strptime(survey_date, '%Y-%m-%d').date()
            if (survey_date > date.today()):
                messages.error(self.request, 'Cannot take survey for future date.')
            else:
                user_obj = self.request.user
                questions = Questions.objects.all()
                if DailySurvey.objects.filter(user = user_obj, date = survey_date).exists():
                    daily_survey_obj = DailySurvey.objects.get(user = user_obj, date = survey_date)
                    survey_response = json.loads(daily_survey_obj.survey)
                else:
                    daily_survey_obj = None
                for i in questions:
                    question_data = {}
                    question_data['id'] = i.id
                    question_data['question'] = i.question
                    question_data['options'] = json.loads(i.options)
                    if daily_survey_obj is not None:
                        question_data['response'] = int(survey_response[str(i.id)])
                    else:
                        question_data['response'] = None
                    data.append(question_data)
        except Exception:
            messages.error(self.request, 'Select correct date.')
        context['questions'] = data
        context['page_title'] = 'Survey'
        return render(self.request, self.template_name, context)

    def post(self, request):
        questions = Questions.objects.all()
        survey_date = self.request.GET.get('survey_date', date.today())
        daily_survey_obj, created = DailySurvey.objects.get_or_create(user = request.user, date = survey_date)
        survey_response = {}
        for i in questions:
            survey_response[i.id] = request.POST.get(str(i.id))
        daily_survey_obj.survey = json.dumps(survey_response)
        daily_survey_obj.save()
        messages.success(self.request, 'Survey response saved.')
        return redirect('user:dashboard')

# API to update profile details
class DailySurveyUpdate(APIView):
    permission_classes = [AllowAny]
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            question = getparameter(request, 'question')
            answer = getparameter(request, 'answer')
            uid = getparameter(request, 'uid')
            if User.objects.filter(id = uid).exists():
                user = User.objects.get(id = uid)
            else:
                response = {'status': 400, 'message': constants.incorrect_uid}
                return Response(response, status = HTTP_400_BAD_REQUEST)
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if Questions.objects.filter(id = question).exists():
            daily_survey_obj, created = DailySurvey.objects.get_or_create(user= user, question_id = question, date = date.today())
            daily_survey_obj.response = answer
            daily_survey_obj.save()
            response = {'status': 200}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.parameter_error}
            return Response(response, status = HTTP_200_OK)
# API to update profile details
class GetForecast(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            location = getparameter(request, 'location')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            data = {}
            data['key'] = WEATHER_API_KEY
            data['q'] = location
            data['days'] = 5
            data['aqi'] = 'yes'
            weather_response = requests.get(WEATHER_API_URL, data)
            forecast = {}
            response_data = {}
            if weather_response.status_code == 200:
                weather_response = json.loads(weather_response.text)
                so2 = weather_response['current']['air_quality']['so2']
                no2 = weather_response['current']['air_quality']['no2']
                location_name = weather_response['location']['name']
                weather_response = weather_response['forecast']['forecastday']
                for i in weather_response:
                    day_forecast = {}
                    day_forecast['avg_temp'] = i['day']['avgtemp_c']
                    day_forecast['avg_humidity'] = i['day']['avghumidity']
                    day_forecast['so2'] = so2
                    day_forecast['no2'] = no2
                    forecast[i['date']] = day_forecast
                response_data['location'] = location_name
                response_data['forecast'] = forecast
            response = {'status': 200, 'data': response_data}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to get survey questions
class GetSurveyDetails(APIView):
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
            questions = Questions.objects.all()
            data = []
            details = {}
            if DailySurvey.objects.filter(user = user_obj, date = survey_date).exists():
                daily_survey_obj = DailySurvey.objects.get(user = user_obj, date = survey_date)
                survey_response = json.loads(daily_survey_obj.survey)
                survey_taken = 1
            else:
                daily_survey_obj = None
                survey_taken = 0
            for i in questions:
                question_data = {}
                question_data['id'] = i.id
                question_data['question'] = i.question
                question_data['options'] = json.loads(i.options)
                if daily_survey_obj is not None:
                    question_data['response'] = int(survey_response[str(i.id)])
                else:
                    question_data['response'] = None
                data.append(question_data)
            response = {'status': 200, 'data': data, 'survey_taken': survey_taken}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to update survey answers
class DailySurveyUpdate(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            survey_date = getparameter(request, 'survey_date')
            answers = getparameter(request, 'answers')
            answers = json.loads(answers)
            if User.objects.filter(id = uid).exists():
                user = User.objects.get(id = uid)
            else:
                response = {'status': 400, 'message': constants.incorrect_uid}
                return Response(response, status = HTTP_400_BAD_REQUEST)
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        transaction.set_autocommit(False)
        try:
            for i, j in answers.items():
                if Questions.objects.filter(id = i).exists():
                    daily_survey_obj, created = DailySurvey.objects.get_or_create(user= user, question_id = i, date = survey_date)
                    daily_survey_obj.response = j
                    daily_survey_obj.save()
            transaction.commit()
            response = {'status': 200}
            return Response(response, status = HTTP_200_OK)
        except Exception:
            transaction.rollback()
            response = {'status': 400, 'message': constants.parameter_error}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to update survey answers
class GetDailyRating(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if SurveyRating.objects.filter(user = user_obj, date = date.today()).exists():
            rating = SurveyRating.objects.get(user = user_obj, date = date.today()).rating
        else:
            rating = 0
        response = {'status': 200, 'rating': rating}
        return Response(response, status = HTTP_200_OK)

class Weather(LoginRequiredMixin, TemplateView):
    template_name = "weather.html"

    def get(self, *args , **kwargs):
        city = self.request.GET.get('city', '')
        forecast = {}
        context = {}
        if city != '':
            data = {}
            data['key'] = WEATHER_API_KEY
            data['q'] = city
            data['days'] = 10
            data['aqi'] = 'yes'
            weather_response = requests.get(WEATHER_API_URL, data)
            forecast = {}
            if weather_response.status_code == 200:
                weather_response = json.loads(weather_response.text)
                so2 = weather_response['current']['air_quality']['so2']
                no2 = weather_response['current']['air_quality']['no2']
                weather_response = weather_response['forecast']['forecastday']
                for i in weather_response:
                    day_forecast = {}
                    day_forecast['avg_temp'] = i['day']['avgtemp_c']
                    day_forecast['avg_humidity'] = i['day']['avghumidity']
                    day_forecast['so2'] = so2
                    day_forecast['no2'] = no2
                    forecast[i['date']] = day_forecast
        context['forecast'] = forecast
        context['page_title'] = 'Weather'
        return render(self.request, self.template_name, context)