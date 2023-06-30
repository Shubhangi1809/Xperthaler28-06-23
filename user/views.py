from traceback import print_tb
from django.contrib.auth.models import User, Group
from django.views.generic import (FormView, UpdateView, TemplateView, DeleteView,
                                  CreateView, ListView)
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import login

from .models import (Allergies, Appointment, Notification, Prescription, UserProfile,
                     UserSocialLink, FirebaseAccount, UserConnection, Pharmacy, EmergencyContact, UserSettings)

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, datetime, timedelta
import pandas as pd
from django.db import transaction
from inhaler.models import Device, Inhalation
import json
from survey.models import SurveyRating, DailySurvey
import os
from django.core.files.base import ContentFile
import base64
from django.dispatch.dispatcher import receiver
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from xperthaler_backend.utils import getparameter
from xperthaler_backend import constants
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from firebase_admin import auth
from .forms import *
from django.db import models
from firebase_admin.exceptions import FirebaseError
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from xperthaler_backend.settings.configuration import firebaseConfig
from django.urls import reverse
from django.http import HttpResponseRedirect

# Deleting firebase account for user when user is deleted from django database


@receiver(models.signals.post_delete, sender=FirebaseAccount)
def delete_firebase_account(sender, instance, *args, **kwargs):
    if instance.uid:
        try:
            auth.delete_user(uid=instance.uid)
        except Exception:
            print("No firebase user with uid:{0}".format(instance.uid))

# Deleting notification if patient removed doctor/caretaker


@receiver(models.signals.post_delete, sender=UserConnection)
def remove_request_notification(sender, instance, *args, **kwargs):
    try:
        Notification.objects.filter(
            object_id=instance.id, content_type=ContentType.objects.get_for_model(UserConnection)).delete()
    except Exception:
        print("Error deleting notification for content:{0}".format(instance))

# View for user login


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_expiry(0)
        request.session.set_test_cookie()
        if request.user.is_authenticated:
            return redirect('user:dashboard')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(LoginView, self).get_context_data(*args, **kwargs)
        context['firebase_config'] = firebaseConfig
        return context

    def form_valid(self, form):
        user = form.get_user()
        if user.is_authenticated:
            login(self.request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
            if user.is_superuser or user.is_staff:
                return redirect('admin:index')
            firebase_account_obj = FirebaseAccount.objects.get(user=user)
            user_profile_obj = UserProfile.objects.get(user=user)
            try:
                auth.update_user(firebase_account_obj.uid, password=form.cleaned_data.get(
                    'password'), phone_number=user_profile_obj.phone_number)
            except Exception:
                pass
            self.request.session['med_type'] = 0
            return redirect('user:dashboard')

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

# View for user registration


class RegisterView(FormView):
    account_type_form = RegistrationAccountTypeForm
    basic_form = RegistrationUserForm
    profile_form = RegistrationUserProfileForm
    template_name = 'register.html'

    def get(self, request,  *kwargs):
        account_type_form = self.account_type_form(None)
        basic_form = self.basic_form(None)
        profile_form = self.profile_form(None)
        return render(request, self.template_name, {'account_type_form': account_type_form, 'basic_form': basic_form, 'profile_form': profile_form})

    def post(self, request,  *kwargs):
        account_type_form = self.account_type_form(request.POST)
        basic_form = self.basic_form(request.POST)
        profile_form = self.profile_form(request.POST)
        if account_type_form.is_valid() and basic_form.is_valid() and profile_form.is_valid():
            first_name = basic_form.cleaned_data.get('first_name')
            last_name = basic_form.cleaned_data.get('last_name')
            email = basic_form.cleaned_data.get('email').lower()
            password = basic_form.cleaned_data.get('password')
            profile_type = account_type_form.cleaned_data.get('profile_type')
            dob = profile_form.cleaned_data.get('dob')
            gender = profile_form.cleaned_data.get('gender')
            phone_number = profile_form.cleaned_data.get('phone_number')
            city = profile_form.cleaned_data.get('city')
            state = profile_form.cleaned_data.get('state')
            country = profile_form.cleaned_data.get('country')
            user_obj, created = User.objects.get_or_create(username=email)
            user_obj.email = email
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.is_active = True
            user_obj.set_password(password)
            user_obj.groups.add(Group.objects.get(id=profile_type))
            user_obj.save()
            user_profile_obj, created = UserProfile.objects.get_or_create(
                user=user_obj)
            user_profile_obj.dob = dob
            user_profile_obj.gender = gender
            user_profile_obj.phone_number = phone_number
            user_profile_obj.city = city
            user_profile_obj.state = state
            user_profile_obj.country = country
            user_profile_obj.save()
            try:
                auth.delete_user(
                    uid=auth.get_user_by_phone_number(phone_number).uid)
            except Exception:
                pass
            UserSocialLink.objects.get_or_create(user=user_obj)
            if FirebaseAccount.objects.filter(user=user_obj).exists():
                print('-----ch---if')
                firebase_account_obj = FirebaseAccount.objects.get(
                    user=user_obj)
                print(firebase_account_obj)
                try:
                    auth.update_user(firebase_account_obj.uid, email=email,
                                     password=password, phone_number=phone_number)
                except Exception as ex:
                    pass
            else:
                print('-----ch---else')
                try:
                    firebase_user = auth.create_user(
                        email=email, password=password, phone_number=phone_number)
                    FirebaseAccount.objects.create(
                        user=user_obj,
                        uid=firebase_user.uid
                    )
                    print(firebase_user)
                except Exception as ex:
                    print('-----ch---Exception')
                    print(ex)
                    pass
            messages.success(request, 'Registration successful. Please login')
            return redirect("user:login")
        else:
            messages.error(request, 'Please check the below errors')
            return render(request, self.template_name, {'account_type_form': account_type_form, 'basic_form': basic_form, 'profile_form': profile_form})


# View for user registration
class CompleteRegistrationView(UpdateView):
    account_type_form = RegistrationAccountTypeForm
    basic_form = FirebaseRegistrationUserForm
    profile_form = RegistrationUserProfileForm
    template_name = 'register.html'

    def get(self, request, *kwargs, pk):
        user_obj = User.objects.get(id=pk)
        user_profile_obj = UserProfile.objects.get(user=user_obj)
        account_type_form = self.account_type_form(instance=user_profile_obj)
        basic_form = self.basic_form(instance=user_obj)
        profile_form = self.profile_form(instance=user_profile_obj)
        return render(request, self.template_name, {'account_type_form': account_type_form, 'basic_form': basic_form, 'profile_form': profile_form})

    def post(self, request, *kwargs, pk):
        account_type_form = self.account_type_form(request.POST)
        basic_form = self.basic_form(request.POST)
        profile_form = self.profile_form(request.POST)
        if account_type_form.is_valid() and basic_form.is_valid() and profile_form.is_valid():
            first_name = basic_form.cleaned_data.get('first_name')
            last_name = basic_form.cleaned_data.get('last_name')
            password = basic_form.cleaned_data.get('password')
            profile_type = account_type_form.cleaned_data.get('profile_type')
            dob = profile_form.cleaned_data.get('dob')
            gender = profile_form.cleaned_data.get('gender')
            phone_number = profile_form.cleaned_data.get('phone_number')
            city = profile_form.cleaned_data.get('city')
            state = profile_form.cleaned_data.get('state')
            country = profile_form.cleaned_data.get('country')
            user_obj = User.objects.get(id=pk)
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.is_active = True
            user_obj.set_password(password)
            user_obj.groups.add(Group.objects.get(id=profile_type))
            user_obj.save()
            user_profile_obj, created = UserProfile.objects.get_or_create(
                user=user_obj)
            user_profile_obj.dob = dob
            user_profile_obj.gender = gender
            user_profile_obj.phone_number = phone_number
            user_profile_obj.city = city
            user_profile_obj.state = state
            user_profile_obj.country = country
            user_profile_obj.save()
            try:
                auth.delete_user(
                    uid=auth.get_user_by_phone_number(phone_number).uid)
            except Exception:
                pass
            firebase_account_obj = FirebaseAccount.objects.get(user=user_obj)
            try:
                auth.update_user(firebase_account_obj.uid,
                                 password=password, phone_number=phone_number)
            except Exception:
                pass
            messages.success(request, 'Registration successful. Please login')
            return redirect("user:login")
        else:
            messages.error(request, 'Please check the below errors')
            return render(request, self.template_name, {'account_type_form': account_type_form, 'basic_form': basic_form, 'profile_form': profile_form})


class LoginPhoneNumberView(FormView):
    form_class = AuthenticationForm
    template_name = 'login_phone.html'
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return render(self.request, self.template_name, {'firebase_config': firebaseConfig})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("user:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, *args, **kwargs):
        self.request.session['refresh'] = 0
        context = super(DashboardView, self).get_context_data(*args, **kwargs)
        if self.request.user.groups.filter(name__in=['Doctor']).exists():
            dashboard_data = get_doctor_dashboarddata(self.request.user)
        elif self.request.user.groups.filter(name__in=['Patient']).exists():
            dashboard_data = get_patient_dashboarddata(
                self.request.user, self.request.session['med_type'])
        elif self.request.user.groups.filter(name__in=['Caretaker']).exists():
            dashboard_data = get_caretaker_dashboarddata(self.request.user)
        context.update(dashboard_data)
        return context


class DashboardAutoRefresh(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, *args, **kwargs):
        self.request.session['refresh'] = 1
        context = super(DashboardAutoRefresh,
                        self).get_context_data(*args, **kwargs)
        if self.request.user.groups.filter(name__in=['Doctor']).exists():
            dashboard_data = get_doctor_dashboarddata(self.request.user)
        elif self.request.user.groups.filter(name__in=['Patient']).exists():
            dashboard_data = get_patient_dashboarddata(
                self.request.user, self.request.session['med_type'])
        elif self.request.user.groups.filter(name__in=['Caretaker']).exists():
            dashboard_data = get_caretaker_dashboarddata(self.request.user)
        context.update(dashboard_data)
        return context


def get_patient_dashboarddata(user, med_type):
    data = {}
    device_details = {'next_inhalation': '', 'last_inhalation': '',
                      'med_name': '', 'dosage_left': '', 'expiry_date': '', 'manufacturer': ''}
    inhalations = []
    if Device.objects.filter(user=user, medicine_type=int(med_type), status=1).exists():
        device_obj = Device.objects.filter(user=user, medicine_type=int(
            med_type), status=1).order_by('-updated')[0]
        device_details['med_name'] = device_obj.medicine_name
        device_details['expiry_date'] = device_obj.expiry_date.strftime(
            '%d-%m-%Y')
        device_details['manufacturer'] = device_obj.company_name
        if Inhalation.objects.filter(device=device_obj).exists():
            last_inhalation_obj = Inhalation.objects.filter(
                device=device_obj).order_by('-updated')[0]
            device_details['dosage_left'] = last_inhalation_obj.count
            device_details['last_inhalation'] = Inhalation.objects.filter(device__user=user, device__medicine_type=int(
                med_type)).order_by('-id')[0].inhalation_time.strftime('%d-%m-%Y %H:%M')
        else:
            device_details['dosage_left'] = device_obj.max_count
    inhalation_objects = Inhalation.objects.filter(
        device__user=user, device__medicine_type=int(med_type)).order_by('-id')[:5]
    if inhalation_objects.exists():
        device_details['last_inhalation'] = inhalation_objects[0].inhalation_time.strftime(
            '%d-%m-%Y %H:%M')
        count = 0
        for inhalation_object in inhalation_objects:
            count = count + 1
            if count < len(inhalation_objects):
                previous_inhalation_time = inhalation_objects[count].inhalation_time
            else:
                previous_inhalation_time = None
            if previous_inhalation_time is not None:
                diff = inhalation_object.inhalation_time - previous_inhalation_time
                interval = str(diff.seconds//3600)+':' + \
                    str((diff.seconds//60) % 60)
            else:
                interval = ''
            inhalations_data = {}
            inhalations_data['date'] = inhalation_object.inhalation_time.strftime(
                '%d-%m-%Y')
            inhalations_data['time'] = inhalation_object.inhalation_time.strftime(
                '%H:%M')
            inhalations_data['interval'] = interval
            inhalations.append(inhalations_data)
    data['device_details'] = device_details
    data['inhalations'] = inhalations
    allergies = UserProfile.objects.get(
        user=user).allergies.all().order_by('name')
    user_allergies = []
    for i in allergies:
        user_allergies.append(i.name)
    data['user_allergies'] = user_allergies
    recommendations = Prescription.objects.filter(
        patient=user).order_by('-date')
    data['recommendations'] = recommendations
    return data


def get_doctor_dashboarddata(user):
    data = {}
    patients = UserConnection.objects.filter(type=0, connection=user).order_by(
        'user__first_name', 'user__last_name')
    data['patients'] = patients
    data['patient_count'] = patients.count()
    appointments = Appointment.objects.filter(
        doctor=user, date=date.today()).order_by('time')
    data['day_appointment_count'] = appointments.count()
    data['appointments'] = appointments
    date_obj = datetime.today()
    start_of_week = date_obj - timedelta(days=date_obj.weekday()+1)
    end_of_week = start_of_week + timedelta(days=6)
    data['week_appointment_count'] = Appointment.objects.filter(
        doctor=user, date__range=(start_of_week, end_of_week)).order_by('time').count()
    return data


def get_caretaker_dashboarddata(user):
    data = {}
    patients = UserConnection.objects.filter(type=1, connection=user).order_by(
        'user__first_name', 'user__last_name')
    data['patients'] = patients
    data['patient_count'] = patients.count()
    appointments = Appointment.objects.filter(patient__in=list(patients.values_list(
        'user', flat=True)), date__gte=date.today()).order_by('date', 'time')
    data['appointments'] = appointments
    return data


class ProfileView(LoginRequiredMixin, UpdateView):
    user_form = UserForm
    profile_form = UserProfileForm
    social_links_form = UserSocialLinksForm
    profile_picture_form = ProfilePictureForm
    template_name = "profile.html"

    def get(self, request, *kwargs):
        user_obj = request.user
        user_profile_obj = UserProfile.objects.get(user=user_obj)
        user_social_links_obj = UserSocialLink.objects.get(user=user_obj)
        user_form = self.user_form(instance=user_obj)
        profile_form = self.profile_form(instance=user_profile_obj)
        profile_picture_form = self.profile_picture_form(
            instance=user_profile_obj)
        social_links_form = self.social_links_form(
            instance=user_social_links_obj)
        data = {}
        data['page_title'] = 'Profile'
        data['user_form'] = user_form
        data['profile_form'] = profile_form
        data['social_links_form'] = social_links_form
        data['user_profile'] = user_profile_obj
        data['profile_picture_form'] = profile_picture_form
        data['user_social_links'] = user_social_links_obj
        return render(request, self.template_name, data)

    def post(self, request, *kwargs):
        user_form = self.user_form(request.POST)
        profile_form = self.profile_form(request.POST)
        profile_picture_form = self.profile_picture_form(request.POST)
        social_links_form = self.social_links_form(request.POST)
        if user_form.is_valid() and profile_form.is_valid() and social_links_form.is_valid():
            user_obj = request.user
            user_profile_obj = UserProfile.objects.get(user=user_obj)
            user_social_links_obj = UserSocialLink.objects.get(user=user_obj)
            email = user_form.cleaned_data['email']
            phone_number = profile_form.cleaned_data['phone_number']
            data = {}
            data['page_title'] = 'Profile'
            data['user_form'] = user_form
            data['profile_form'] = profile_form
            data['social_links_form'] = social_links_form
            data['user_profile'] = user_profile_obj
            data['profile_picture_form'] = profile_picture_form
            data['user_social_links'] = user_social_links_obj
            if User.objects.filter(username=email).exclude(id=self.request.user.id).exists():
                messages.error(request, 'Email linked to another user.')
                return render(request, self.template_name, data)
            if UserProfile.objects.filter(phone_number=phone_number).exclude(user=self.request.user).exists():
                messages.error(request, 'Phone number linked to another user.')
                return render(request, self.template_name, data)
            firebase_account_obj = FirebaseAccount.objects.get(user=user_obj)
            if email != user_obj.email:
                try:
                    auth.delete_user(uid=firebase_account_obj.uid)
                    firebase_user = auth.create_user(
                        email=email, phone_number=phone_number)
                    firebase_account_obj.uid = firebase_user.uid
                    firebase_account_obj.save()
                except Exception:
                    pass
            elif email == user_obj.email and phone_number != user_profile_obj.phone_number:
                try:
                    auth.update_user(firebase_account_obj.uid,
                                     phone_number=phone_number)
                except Exception:
                    pass
            user_obj.first_name = user_form.cleaned_data['first_name']
            user_obj.last_name = user_form.cleaned_data['last_name']
            user_obj.username = user_form.cleaned_data['email']
            user_obj.email = user_form.cleaned_data['email']
            user_obj.save()
            user_profile_obj.dob = profile_form.cleaned_data['dob']
            user_profile_obj.gender = profile_form.cleaned_data['gender']
            user_profile_obj.height = profile_form.cleaned_data['height']
            user_profile_obj.weight = profile_form.cleaned_data['weight']
            user_profile_obj.blood_group = profile_form.cleaned_data['blood_group']
            user_profile_obj.phone_number = profile_form.cleaned_data['phone_number']
            user_profile_obj.country = profile_form.cleaned_data['country']
            user_profile_obj.city = profile_form.cleaned_data['city']
            user_profile_obj.state = profile_form.cleaned_data['state']
            user_profile_obj.notification_status = profile_form.cleaned_data[
                'notification_status']
            user_profile_obj.save()
            user_social_links_obj.facebook = social_links_form.cleaned_data['facebook']
            user_social_links_obj.twitter = social_links_form.cleaned_data['twitter']
            user_social_links_obj.linkedin = social_links_form.cleaned_data['linkedin']
            user_social_links_obj.instagram = social_links_form.cleaned_data['instagram']
            user_social_links_obj.save()
            messages.success(request, 'Profile updated.')
            return redirect('user:profile')
        else:
            messages.error(request, 'Please check the below errors')
            user_obj = request.user
            user_profile_obj = UserProfile.objects.get(user=user_obj)
            user_social_links_obj = UserSocialLink.objects.get(user=user_obj)
            data = {}
            data['page_title'] = 'Profile'
            data['user_form'] = user_form
            data['profile_form'] = profile_form
            data['social_links_form'] = social_links_form
            data['user_profile'] = user_profile_obj
            data['profile_picture_form'] = profile_picture_form
            data['user_social_links'] = user_social_links_obj
            return render(request, self.template_name, data)


def chat(request):
    context = {}
    context['page_title'] = 'Chat'
    return render(request, 'chat.html', context)


class UserConnectionsView(LoginRequiredMixin, TemplateView):
    template_name = "user_connections.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserConnectionsView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = _('Add doctor / Caretaker')
        doctors_list = []
        caretakers_list = []
        doctors = UserConnection.objects.filter(user=self.request.user).exclude(
            status=2).order_by('connection__first_name', 'connection__last_name')
        for i in doctors:
            details = {}
            details['id'] = i.id
            details['name'] = i.connection.first_name + \
                ' '+i.connection.last_name
            details['email'] = i.connection.email
            details['phone_number'] = UserProfile.objects.get(
                user=i.connection).phone_number
            if i.status == 0:
                details['status'] = _('Requested')
            elif i.status == 1:
                details['status'] = _('Active')
            if i.type == 0:
                doctors_list.append(details)
            else:
                caretakers_list.append(details)
        context['doctors_list'] = doctors_list
        context['caretakers_list'] = caretakers_list
        context['pharmacies'] = Pharmacy.objects.filter(
            user=self.request.user).order_by('name')
        context['emergency_contact'] = EmergencyContact.objects.filter(
            user=self.request.user).order_by('name')
        return context


class MapView(LoginRequiredMixin, TemplateView):
    template_name = "maps.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MapView, self).get_context_data(*args, **kwargs)
        context['page_title'] = 'Maps'
        return context


def preferences(request):
    data = {}
    data['page_title'] = "Preferences"
    return render(request, 'preferences.html', data)


class EditPreferencesView(LoginRequiredMixin, UpdateView):
    form_class = PreferencesForm
    template_name = "preferences.html"
    title = _('Preferences')
    success_url = '/preferences'

    def get_object(self, queryset=None):
        return UserSettings.objects.get(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super(EditPreferencesView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Preferences updated.'))
        return redirect('user:preferences')


def help(request):
    data = {}
    data['page_title'] = "Help"
    return render(request, 'help.html', data)

# API to login


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = getparameter(request, 'username')
            password = getparameter(request, 'password')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is None:
            response = {'status': 400, 'message': constants.login_failed}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        response = {'status': 200, 'user_id': user.id, 'name': user.first_name, 'role': 1,
                    'rating': 5, 'auth_token': token.key, 'message': constants.login_success}
        return Response(response, status=HTTP_200_OK)

# API to get user details


class GetUserDetails(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(id=uid).exists():
            user_obj = User.objects.get(id=uid)
            user_profile_obj = UserProfile.objects.get(user=user_obj)
            user_social_obj, created = UserSocialLink.objects.get_or_create(
                user=user_obj)
            response = {}
            response['name'] = user_obj.first_name if user_obj.first_name else ''
            response['email'] = user_obj.email if user_obj.email else ''
            response['gender'] = user_profile_obj.gender
            response['height'] = user_profile_obj.height if user_profile_obj.height else ''
            response['weight'] = user_profile_obj.weight if user_profile_obj.weight else ''
            response['blood_group'] = user_profile_obj.blood_group
            if user_profile_obj.blood_group is not None:
                response['blood_group_name'] = constants.BLOOD_GROUP_CHOICES[user_profile_obj.blood_group][1]
            else:
                response['blood_group_name'] = ''
            response['phone_number'] = user_profile_obj.phone_number if user_profile_obj.phone_number else ''
            response['city'] = user_profile_obj.city if user_profile_obj.city else ''
            response['state'] = user_profile_obj.state if user_profile_obj.state else ''
            response['country'] = user_profile_obj.country if user_profile_obj.country else ''
            response['notification_status'] = user_profile_obj.notification_status
            response['user_allergies'] = list(
                user_profile_obj.allergies.values_list('id', flat=True))
            response['facebook_url'] = user_social_obj.facebook if user_social_obj.facebook else ''
            response['twitter_url'] = user_social_obj.twitter if user_social_obj.twitter else ''
            response['linkedin_url'] = user_social_obj.linkedin if user_social_obj.linkedin else ''
            response['instagram_url'] = user_social_obj.instagram if user_social_obj.instagram else ''
            if user_profile_obj.profile_picture_original is not None and user_profile_obj.profile_picture_original != '':
                response['profile_picture'] = user_profile_obj.profile_picture_original.url
            else:
                response['profile_picture'] = ''
            response = {'status': 200, 'user_details': response}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status=HTTP_400_BAD_REQUEST)

# API to get profile details


class GetAllergiesList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        allergies = Allergies.objects.all()
        allergies_list = {}
        for i in allergies:
            allergies_list[i.id] = i.name
        response = {'status': 200, 'allergies_list': allergies_list}
        return Response(response, status=HTTP_200_OK)

# API to update profile details


class UpdateUserProfile(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            name = request.data.get('name', '')
            email = request.data.get('email', '')
            gender = request.data.get('gender', '')
            height = request.data.get('height', '')
            weight = request.data.get('weight', '')
            blood_group = request.data.get('blood_group', '')
            phone_number = request.data.get('phone_number', '')
            city = request.data.get('city', '')
            state = request.data.get('state', '')
            country = request.data.get('country', '')
            allergies = request.data.get('allergies', '')
            allergies = json.loads(allergies)
            notification_status = request.data.get(
                'notification_status', False)
            if notification_status == 'true':
                notification_status = True
            else:
                notification_status = False
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(id=uid).exists():
            user_obj = User.objects.get(id=uid)
            user_obj.first_name = name
            user_obj.email = email
            user_obj.save()
            user_profile_obj = UserProfile.objects.get(user=user_obj)
            user_profile_obj.gender = gender
            user_profile_obj.height = height
            user_profile_obj.weight = weight
            if blood_group != '':
                user_profile_obj.blood_group = blood_group
            user_profile_obj.phone_number = phone_number
            user_profile_obj.city = city
            user_profile_obj.state = state
            user_profile_obj.country = country
            user_profile_obj.notification_status = notification_status
            user_profile_obj.allergies.set(allergies)
            user_profile_obj.save()
            response = {'status': 200}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status=HTTP_400_BAD_REQUEST)

# API to update profile details


class UpdateUserLinks(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            facebook = request.data.get('facebook', '')
            twitter = request.data.get('twitter', '')
            linkedin = request.data.get('linkedin', '')
            instagram = request.data.get('instagram', '')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(id=uid).exists():
            user_obj = User.objects.get(id=uid)
            user_social_obj, created = UserSocialLink.objects.get_or_create(
                user=user_obj)
            user_social_obj.facebook = facebook
            user_social_obj.twitter = twitter
            user_social_obj.linkedin = linkedin
            user_social_obj.instagram = instagram
            user_social_obj.save()
            response = {'status': 200, 'message': 'Success'}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status=HTTP_400_BAD_REQUEST)


class GetUsersList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = users = User.objects.all()
        user_list = {}
        for i in users:
            user_list[i.id] = i.first_name
        response = {'status': 200, 'user_list': user_list}
        return Response(response, status=HTTP_200_OK)


class UploadExcel(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        file = request.data.get('file', None)
        # file_path = 'media/' + datetime.today().strftime("%Y-%m-%d:%H:%M:%S")+file.name
        BASE_DIR = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        file_path = BASE_DIR + '/src/media/' + \
            datetime.today().strftime("%Y-%m-%d:%H:%M:%S")+file.name
        with open(file_path, 'wb') as file_obj:
            file_obj.write(file.read())
            file_obj.close()
        processfile(file_path)
        response = {'status': 200}
        return Response(response, status=HTTP_200_OK)


def processfile(file):
    data = pd.read_csv(file).to_dict('records')
    transaction.set_autocommit(False)
    try:
        for i in data:
            uid = i['uid']
            device_name = i['device_name']
            location = i['location']
            medicine_name = i['medicine_name']
            medicine_type = i['medicine_type']
            inhalation_time = i['inhalation_time']
            expiry_date = i['expiry_date']
            count = i['count']
            angle = i['angle']
            shaken = i['shaken']
            if User.objects.filter(id=uid).exists():
                user_obj = User.objects.get(id=uid)
                create_new_device_obj = False
                if Device.objects.filter(device_name=device_name, status=1).exists():
                    device_obj = Device.objects.get(
                        device_name=device_name, status=1)
                    if device_obj.user != user_obj or device_obj.medicine_name != medicine_name or device_obj.medicine_type != int(medicine_type):
                        device_obj.status = 0
                        device_obj.save()
                        create_new_device_obj = True
                    else:
                        device_obj.count = count
                        device_obj.save()
                else:
                    create_new_device_obj = True
                if create_new_device_obj:
                    device_obj = Device.objects.create(
                        user=user_obj,
                        device_name=device_name,
                        medicine_name=medicine_name,
                        medicine_type=medicine_type,
                        expiry_date=expiry_date,
                        count=count,
                        status=1,
                    )
                Inhalation.objects.create(
                    user=user_obj,
                    device=device_obj,
                    location=location,
                    inhalation_time=inhalation_time,
                    angle=angle,
                    shaken=shaken,
                )
            else:
                continue
        transaction.commit()
        response = {'status': 200}
        return Response(response, status=HTTP_200_OK)
    except Exception:
        transaction.rollback()
        response = {'status': 400, 'message': constants.parameter_error}
        return Response(response, status=HTTP_400_BAD_REQUEST)

# API to get user dashboard data


class DashboardData(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            med_type = getparameter(request, 'med_type')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(id=uid).exists():
            data = {}
            device_details = {'next_inhalation': '', 'last_inhalation': '',
                              'med_name': '', 'dosage_left': '', 'expiry_date': '', 'manufacturer': ''}
            inhalations = []
            user_obj = User.objects.get(id=uid)
            if Device.objects.filter(user=user_obj, medicine_type=int(med_type), status=1).exists():
                device = Device.objects.filter(user=user_obj, medicine_type=int(
                    med_type), status=1).order_by('-updated')[0]
                device_details['med_name'] = device.medicine_name
                device_details['expiry_date'] = device.expiry_date.strftime(
                    '%d-%m-%Y')
                device_details['dosage_left'] = device.count
            inhalation_objects = Inhalation.objects.filter(
                user=user_obj, device__medicine_type=int(med_type)).order_by('-id')[:5]
            if inhalation_objects.exists():
                device_details['last_inhalation'] = inhalation_objects[0].inhalation_time.strftime(
                    '%d-%m-%Y %H:%M')
                count = 0
                for inhalation_object in inhalation_objects:
                    count = count + 1
                    if count < len(inhalation_objects):
                        previous_inhalation_time = inhalation_objects[count].inhalation_time
                    else:
                        previous_inhalation_time = None
                    if previous_inhalation_time is not None:
                        diff = inhalation_object.inhalation_time - previous_inhalation_time
                        interval = str(diff.seconds//3600)+':' + \
                            str((diff.seconds//60) % 60)
                    else:
                        interval = ''
                    inhalations_data = {}
                    inhalations_data['date'] = inhalation_object.inhalation_time.strftime(
                        '%d-%m-%Y')
                    inhalations_data['time'] = inhalation_object.inhalation_time.strftime(
                        '%H:%M')
                    inhalations_data['interval'] = interval
                    inhalations.append(inhalations_data)
            data['device_details'] = device_details
            data['inhalations'] = inhalations
            response = {'status': 200, 'data': data}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status=HTTP_400_BAD_REQUEST)

# API to get logged in user details for frontend session


class GetLoggedInUserDetails(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(id=uid).exists():
            user_obj = User.objects.get(id=uid)
            response = {}
            token, created = Token.objects.get_or_create(user=user_obj)
            response['user_id'] = user_obj.id
            response['name'] = user_obj.first_name
            response['first_name'] = user_obj.first_name
            response['last_name'] = user_obj.last_name
            response['auth_token'] = token.key
            response['role'] = 1
            if SurveyRating.objects.filter(user=user_obj, date=date.today()).exists():
                rating = SurveyRating.objects.get(
                    user=user_obj, date=date.today()).rating
            else:
                rating = 0
            response['rating'] = rating
            response = {'status': 200, 'user_details': response}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status=HTTP_400_BAD_REQUEST)

# API to get logged in user details for frontend session


class UpdateProfilePicture(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            image_blob = getparameter(request, 'image')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if User.objects.filter(id=uid).exists():
            user_obj = User.objects.get(id=uid)
            user_profile_obj = UserProfile.objects.get(user=user_obj)

            image_data = image_blob
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr))
            file_name = "'myphoto." + ext
            user_profile_obj.picture_original.save(file_name, data, save=True)
            user_profile_obj.save()
            response = {}
            response = {'status': 200, 'message': constants.profile_pic_update}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status=HTTP_400_BAD_REQUEST)

# API for signin/signup using firebase


class FirebaseSave(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            login_type = int(getparameter(request, 'login_type'))
            if login_type == 1:
                email = getparameter(request, 'email')
        except Exception:
            response = {'message': constants.missing_parameter}
            return Response(response, status=HTTP_400_BAD_REQUEST)
        if FirebaseAccount.objects.filter(uid=uid).exists():
            firebase_account_obj = FirebaseAccount.objects.get(uid=uid)
            user_obj = firebase_account_obj.user
            if user_obj.is_active:
                user_profile_obj = UserProfile.objects.get(user=user_obj)
                if login_type == 1:
                    try:
                        auth.update_user(
                            firebase_account_obj.uid, phone_number=user_profile_obj.phone_number)
                    except Exception:
                        pass
                auth_login(request, user_obj)
                response = {'redirect_type': 1}
                return Response(response, status=HTTP_200_OK)
        elif login_type == 1:
            user_obj = User.objects.create(
                username=email, email=email, is_active=False)
            UserProfile.objects.create(user=user_obj)
            UserSocialLink.objects.create(user=user_obj)
            firebase_account_obj = FirebaseAccount.objects.create(
                user=user_obj, uid=uid)
        if login_type == 1:
            response = {'redirect_type': 2, 'user_id': user_obj.id}
            return Response(response, status=HTTP_200_OK)
        else:
            response = {'redirect_type': 3}
            return Response(response, status=HTTP_200_OK)


@csrf_exempt
def firebaseloginredirect(request):
    redirect_type = request.POST['redirect_type']
    if redirect_type == 1 or redirect_type == '1':
        request.session['refresh'] = 0
        request.session['med_type'] = 0
        return redirect('home')
    elif redirect_type == 2 or redirect_type == '2':
        user_id = request.POST['user_id']
        messages.error(request, 'Please complete your registration.')
        return redirect('user:complete-registration', pk=user_id)
    elif redirect_type == 3 or redirect_type == '3':
        messages.error(request, 'Account not found. Please register.')
        return redirect('home')


def saveprofilepicture(request):
    if request.FILES.get('avatar') is not None:
        user_profile_obj = UserProfile.objects.get(user=request.user)
        user_profile_obj.avatar = request.FILES.get('avatar')
        user_profile_obj.avatar_thumbnail = request.FILES.get('avatar')
        user_profile_obj.save()
        messages.success(request, 'Profile picture updated.')
    return redirect('user:profile')


class EditAllergiesView(LoginRequiredMixin, FormView):
    allergies_form = AllergiesForm
    template_name = "edit_allergies.html"

    def get(self, request, **kwargs):
        data = {}
        data['page_title'] = 'Edit allergies'
        allergies = UserProfile.objects.get(
            user=request.user).allergies.all().order_by('name')
        user_allergies = []
        for i in allergies:
            user_allergies.append((i.key, i.name))
        data['user_allergies'] = user_allergies
        return render(request, self.template_name, data)

    def post(self, request, **kwargs):
        values = dict(request.POST)
        user_profile_obj = UserProfile.objects.get(user=request.user)
        allergies = values['allergies']
        user_profile_obj.allergies.clear()
        for i in allergies:
            allergy_name = i
            allergy_key = allergy_name.replace(' ', '_').lower()
            if Allergies.objects.filter(key=allergy_key).exists():
                allergy = Allergies.objects.get(key=allergy_key)
            else:
                allergy = Allergies.objects.create(
                    key=allergy_key, name=allergy_name)
            user_profile_obj.allergies.add(allergy)
            user_profile_obj.save()
        messages.success(request, 'Allergies updated.')
        return redirect('user:edit-allergies')


class PatientsView(LoginRequiredMixin, ListView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'patients.html'
    model = UserConnection
    paginate_by = 10

    def get_queryset(self, **kwargs):
        if self.request.user.groups.filter(name='Doctor').exists():
            patients = UserConnection.objects.filter(
                type=0, connection=self.request.user).order_by('user__first_name', 'user__last_name')
        else:
            patients = UserConnection.objects.filter(
                type=1, connection=self.request.user).order_by('user__first_name', 'user__last_name')
        return patients

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name='Doctor').exists():
            context['page_title'] = _('Patients')
        else:
            context['page_title'] = _('Relatives/Friends List')
        return context


class AddDoctorView(LoginRequiredMixin, FormView):
    add_doctor_form = AddDoctorForm
    template_name = "add_doctor.html"
    title = _('Add doctors')

    def get(self, request,  *kwargs):
        data = {}
        data['page_title'] = self.title
        data['add_doctor_form'] = self.add_doctor_form(None)
        return render(request, self.template_name, data)

    def post(self, request, **kwargs):
        add_doctor_form = self.add_doctor_form(request.POST)
        doctor_obj = ''
        if add_doctor_form.is_valid():
            doctor = add_doctor_form.cleaned_data.get('doctor')
            if User.objects.filter(email=doctor).exists():
                doctor_obj = User.objects.get(email=doctor)
            else:
                try:
                    if User.objects.filter(id=int(doctor)).exists():
                        doctor_obj = User.objects.get(id=int(doctor))
                except Exception:
                    messages.error(request, _('Doctor not found.'))
            if doctor_obj.groups.filter(name='Doctor').exists():
                if doctor_obj:
                    if UserConnection.objects.filter(user=request.user, connection=doctor_obj).exclude(status=2).exists():
                        messages.error(request, _(
                            'Cannot add same doctor twice.'))
                    else:
                        user_connection_obj = UserConnection.objects.create(
                            user=request.user,
                            connection=doctor_obj,
                            type=0,
                            status=0,
                        )
                        Notification.objects.create(
                            user=doctor_obj,
                            type=0,
                            content_type=ContentType.objects.get_for_model(
                                UserConnection),
                            object_id=user_connection_obj.id
                        )
                        messages.success(request, _('Request sent to doctor.'))
                        return redirect('user:user-connections')
            else:
                messages.error(request, _('Doctor not found.'))
        else:
            messages.error(request, _('Please check the below errors'))
        data = {}
        data['page_title'] = self.title
        data['add_doctor_form'] = add_doctor_form
        return render(request, self.template_name, data)


class RemoveDoctorView(LoginRequiredMixin, DeleteView):
    model = UserConnection
    success_url = '/user-connections'
    template_name = "delete.html"
    title = _('Remove doctor')
    success_message = _("Doctor removed.")

    def get_queryset(self):
        return UserConnection.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(RemoveDoctorView, self).get_context_data(
            *args, **kwargs)
        context['warning'] = _('Are you sure you want to remove this doctor?')
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(RemoveDoctorView, self).delete(request, *args, **kwargs)


class AddCaretakerView(LoginRequiredMixin, FormView):
    add_caretaker_form = AddCaretakerForm
    template_name = "add_caretaker.html"
    title = _('Add caretaker')

    def get(self, request,  *kwargs):
        data = {}
        data['page_title'] = self.title
        data['add_caretaker_form'] = self.add_caretaker_form(None)
        return render(request, self.template_name, data)

    def post(self, request, **kwargs):
        add_caretaker_form = self.add_caretaker_form(request.POST)
        caretaker_obj = ''
        if add_caretaker_form.is_valid():
            caretaker = add_caretaker_form.cleaned_data.get('caretaker')
            if User.objects.filter(email=caretaker).exists():
                caretaker_obj = User.objects.get(email=caretaker)
            else:
                try:
                    if User.objects.filter(id=int(caretaker)).exists():
                        caretaker_obj = User.objects.get(id=int(caretaker))
                except Exception:
                    messages.error(request, _('Caretaker not found.'))
            if caretaker_obj.groups.filter(name='Caretaker').exists():
                if caretaker_obj:
                    if UserConnection.objects.filter(user=request.user, connection=caretaker_obj).exclude(status=2).exists():
                        messages.error(request, _(
                            'Cannot add same caretaker twice.'))
                    else:
                        user_connection_obj = UserConnection.objects.create(
                            user=request.user,
                            connection=caretaker_obj,
                            type=1,
                            status=0,
                        )
                        Notification.objects.create(
                            user=caretaker_obj,
                            type=1,
                            content_type=ContentType.objects.get_for_model(
                                UserConnection),
                            object_id=user_connection_obj.id
                        )
                        messages.success(request, _(
                            'Request sent to caretaker.'))
                        return redirect('user:user-connections')
            else:
                messages.error(request, _('Caretaker not found.'))
        else:
            messages.error(request, _('Please check the below errors'))
        data = {}
        data['page_title'] = self.title
        data['add_caretaker_form'] = add_caretaker_form
        return render(request, self.template_name, data)


class RemoveCaretakerView(LoginRequiredMixin, DeleteView):
    model = UserConnection
    success_url = '/user-connections'
    template_name = "delete.html"
    title = _('Remove caretaker')
    success_message = _("Caretaker removed.")

    def get_queryset(self):
        return UserConnection.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(RemoveCaretakerView,
                        self).get_context_data(*args, **kwargs)
        context['warning'] = _(
            'Are you sure you want to remove this caretaker?')
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(RemoveCaretakerView, self).delete(request, *args, **kwargs)


class AddPharmacyView(LoginRequiredMixin, CreateView):
    form_class = PharmacyForm
    template_name = "add_pharmacy.html"
    title = _('Add pharmacy')

    def get_context_data(self, *args, **kwargs):
        context = super(AddPharmacyView, self).get_context_data(
            *args, **kwargs)
        context['page_title'] = self.title
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        Pharmacy.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            user=self.request.user,
        )
        messages.success(self.request, _('Pharmacy details added.'))
        return redirect('user:user-connections')


class EditPharmacyView(LoginRequiredMixin, UpdateView):
    form_class = PharmacyForm
    template_name = "add_pharmacy.html"
    title = _('Edit pharmacy')
    success_url = '/user-connections'

    def get_object(self, queryset=None):
        return Pharmacy.objects.get(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(EditPharmacyView, self).get_context_data(
            *args, **kwargs)
        context['page_title'] = self.title
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        Pharmacy.objects.filter(id=self.kwargs['pk']).update(
            name=name,
            email=email,
            phone_number=phone_number,
        )
        messages.success(self.request, _('Pharmacy details updated.'))
        return redirect('user:user-connections')


class DeletePharmacyView(LoginRequiredMixin, DeleteView):
    model = Pharmacy
    success_url = '/user-connections'
    template_name = "delete.html"
    title = _('Delete pharmacy')
    success_message = _("Pharmacy deleted.")

    def get_queryset(self):
        return Pharmacy.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DeletePharmacyView, self).get_context_data(
            *args, **kwargs)
        context['warning'] = _(
            'Are you sure you want to delete this pharmacy?')
        context['page_title'] = self.title
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeletePharmacyView, self).delete(request, *args, **kwargs)


class AddEmergencyContactView(LoginRequiredMixin, CreateView):
    form_class = EmergencyContactForm
    template_name = "add_emergency_contact.html"
    title = _('Add emergency contact')

    def get_context_data(self, *args, **kwargs):
        context = super(AddEmergencyContactView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        EmergencyContact.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            user=self.request.user,
        )
        messages.success(self.request, _('Emergency contact details added.'))
        return redirect('user:user-connections')


class EditEmergencyContactView(LoginRequiredMixin, UpdateView):
    form_class = EmergencyContactForm
    template_name = "add_pharmacy.html"
    title = _('Edit emergency contact')
    success_url = '/user-connections'

    def get_object(self, queryset=None):
        return EmergencyContact.objects.get(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(EditEmergencyContactView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        EmergencyContact.objects.filter(id=self.kwargs['pk']).update(
            name=name,
            email=email,
            phone_number=phone_number,
        )
        messages.success(self.request, _('Emergency contact details updated.'))
        return redirect('user:user-connections')


class DeleteEmergencyContactView(LoginRequiredMixin, DeleteView):
    model = EmergencyContact
    success_url = '/user-connections'
    template_name = "delete.html"
    title = _('Remove emergenct contact')
    success_message = _("Emergenct contact deleted.")

    def get_queryset(self):
        return EmergencyContact.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteEmergencyContactView,
                        self).get_context_data(*args, **kwargs)
        context['warning'] = _(
            'Are you sure you want to delete this emergency contact?')
        context['page_title'] = self.title
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteEmergencyContactView, self).delete(request, *args, **kwargs)


class NotificationsView(LoginRequiredMixin, ListView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'notifications.html'
    model = Notification

    def get_queryset(self, **kwargs):
        notifications = Notification.objects.filter(
            user=self.request.user, delete_status=False)
        return notifications

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Notifications')
        return context


class ViewNotificationView(LoginRequiredMixin, TemplateView):
    template_name = 'view_notification.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ViewNotificationView,
                        self).get_context_data(*args, **kwargs)
        notification = Notification.objects.get(id=self.kwargs['pk'])
        notification.view_status = 1
        notification.save()
        if notification.type == 0 or notification.type == 1:
            content_type = notification.content_type
            obj = content_type.get_object_for_this_type(
                pk=notification.object_id)
            context['requested_user'] = obj.user
        context['notification'] = notification
        context['page_title'] = _('View notification')
        return context


def approve_notification(request, pk):
    notification = Notification.objects.get(id=pk)
    if notification.delete_status:
        messages.error(request, _('Invalid operation'))
    if notification.type == 0 or notification.type == 1:
        content_type = notification.content_type
        obj = content_type.get_object_for_this_type(pk=notification.object_id)
        obj.status = 1
        obj.save()
        notification.delete_status = 1
        notification.view_status = 1
        notification.save()
        messages.success(request, _('Accepted'))
    return redirect('user:notifications')

    # pass


def reject_notification(request, pk):
    notification = Notification.objects.get(id=pk)
    if notification.delete_status:
        messages.error(request, _('Invalid operation'))
    if notification.type == 0 or notification.type == 1:
        content_type = notification.content_type
        obj = content_type.get_object_for_this_type(pk=notification.object_id)
        obj.status = 2
        obj.save()
        notification.delete_status = 1
        notification.view_status = 1
        notification.save()
        messages.success(request, _('Rejected'))
    return redirect('user:notifications')


def mark_all_read(request):
    Notification.objects.filter(user=request.user).update(view_status=True)
    messages.success(request, _('Updated'))
    return redirect('user:notifications')


class PatientDetailsView(LoginRequiredMixin, TemplateView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'patient_details.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PatientDetailsView, self).get_context_data(
            *args, **kwargs)
        patient_obj = User.objects.get(id=self.kwargs['pk'])
        patient_profile_obj = UserProfile.objects.get(user=patient_obj)
        context['page_title'] = _('Patient details')
        context['patient_obj'] = patient_obj
        context['patient_profile_obj'] = patient_profile_obj
        allergies = UserProfile.objects.get(
            user=patient_obj).allergies.all().order_by('name')
        patient_allergies = []
        for i in allergies:
            patient_allergies.append(i.name)
        context['patient_allergies'] = patient_allergies
        return context


class AppointmentsListView(LoginRequiredMixin, ListView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'appointments_list.html'
    model = Appointment
    paginate_by = 10

    def get_queryset(self, **kwargs):
        appointments = Appointment.objects.filter(
            doctor=self.request.user, patient_id=self.kwargs['pk']).order_by('date', 'time')
        return appointments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Appointments')
        context['id'] = self.kwargs['pk']
        return context


class AddAppointmentView(LoginRequiredMixin, CreateView):
    form_class = AppointmentForm
    template_name = "add_appointment.html"
    title = _('Add Appointment')

    def get_context_data(self, *args, **kwargs):
        context = super(AddAppointmentView, self).get_context_data(
            *args, **kwargs)
        context['page_title'] = self.title
        context['id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        symptoms = form.cleaned_data.get('symptoms')
        date = form.cleaned_data.get('date')
        time = form.cleaned_data.get('time')
        Appointment.objects.create(
            patient=User.objects.get(id=self.kwargs['pk']),
            doctor=self.request.user,
            symptoms=symptoms,
            date=date,
            time=time,
        )
        messages.success(self.request, _('Appointment saved.'))
        redirect_type = self.kwargs['redirect_type']
        if int(redirect_type):
            return redirect('user:calendar')
        else:
            return redirect('user:appointments', self.kwargs['pk'])


class EditAppointmentView(LoginRequiredMixin, UpdateView):
    form_class = AppointmentForm
    template_name = "edit_appointment.html"
    title = _('Edit Appointment')

    def get_object(self, queryset=None):
        return Appointment.objects.get(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(EditAppointmentView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        return context

    def form_valid(self, form):
        symptoms = form.cleaned_data.get('symptoms')
        date = form.cleaned_data.get('date')
        time = form.cleaned_data.get('time')
        Appointment.objects.filter(id=self.kwargs['pk']).update(
            symptoms=symptoms,
            date=date,
            time=time,
        )
        appointment_obj = Appointment.objects.get(id=self.kwargs['pk'])
        appointment_obj.symptoms = symptoms
        appointment_obj.date = date
        appointment_obj.time = time
        appointment_obj.save()
        messages.success(self.request, _('Appointment saved.'))
        redirect_type = self.kwargs['redirect_type']
        if int(redirect_type):
            return redirect('user:calendar')
        else:
            return redirect('user:appointments', appointment_obj.patient.id)


class DeleteAppointmentView(LoginRequiredMixin, DeleteView):
    model = Appointment
    success_url = '/calendar'
    template_name = "delete.html"
    title = _('Remove appointment')
    success_message = _("Appointment removed.")

    def get_queryset(self):
        return Appointment.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DeleteAppointmentView,
                        self).get_context_data(*args, **kwargs)
        context['warning'] = _(
            'Are you sure you want to remove this appointment?')
        context['page_title'] = self.title
        return context

    def delete(self, request, *args, **kwargs):
        appointment_obj = Appointment.objects.get(id=self.kwargs['pk'])
        patient = appointment_obj.patient
        appointment_obj.delete()
        messages.success(self.request, self.success_message)
        redirect_type = self.kwargs['redirect_type']
        if int(redirect_type):
            return HttpResponseRedirect(reverse('user:calendar'))
        else:
            return HttpResponseRedirect(reverse('user:appointments', kwargs={'pk': patient.id}))


class CalendarView(LoginRequiredMixin, ListView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'calendar.html'
    model = Notification
    paginate_by = 10

    def get_queryset(self, **kwargs):
        appointments = Appointment.objects.filter(
            doctor=self.request.user, date__gte=date.today()).order_by('date', 'time')
        return appointments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(doctor=self.request.user)
        appointment_data = []
        for i in appointments:
            appointment_details = {}
            appointment_details["title"] = i.patient.first_name + \
                ' ' + i.patient.last_name
            appointment_details['start'] = i.date.strftime(
                "%Y-%m-%d") + ' ' + str(i.time)
            appointment_data.append(appointment_details)
        context['appointments'] = appointment_data
        context['page_title'] = _('View notification')
        return context


class PrescriptionsListView(LoginRequiredMixin, ListView):
    '''This view is to handle template which is responsible for manage companies in the model'''
    template_name = 'prescriptions_list.html'
    model = Prescription
    paginate_by = 10

    def get_queryset(self, **kwargs):
        prescriptions = Prescription.objects.filter(
            doctor=self.request.user, patient_id=self.kwargs['pk']).order_by('-date')
        return prescriptions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Prescriptions')
        context['id'] = self.kwargs['pk']
        return context


class AddPrescriptionView(LoginRequiredMixin, CreateView):
    form_class = PrescriptionForm
    template_name = "add_prescription.html"
    title = _('Add Prescription')

    def get_context_data(self, *args, **kwargs):
        context = super(AddPrescriptionView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        context['id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        prescription = form.cleaned_data.get('prescription')
        Prescription.objects.create(
            patient=User.objects.get(id=self.kwargs['pk']),
            doctor=self.request.user,
            prescription=prescription,
        )
        messages.success(self.request, _('Prescription added.'))
        return redirect('user:prescriptions', self.kwargs['pk'])


class EditPrescriptionView(LoginRequiredMixin, UpdateView):
    form_class = PrescriptionForm
    template_name = "add_prescription.html"
    title = _('Edit Prescription')

    def get_object(self, queryset=None):
        return Prescription.objects.get(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(EditPrescriptionView,
                        self).get_context_data(*args, **kwargs)
        context['page_title'] = self.title
        context['id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        prescription = form.cleaned_data.get('prescription')
        prescription_obj = Prescription.objects.get(id=self.kwargs['pk'])
        prescription_obj.prescription = prescription
        prescription_obj.save()
        messages.success(self.request, _('Prescription updated.'))
        return redirect('user:prescriptions', prescription_obj.patient.id)


class DeletePrescriptionView(LoginRequiredMixin, DeleteView):
    model = Prescription
    success_url = '/dashboard'
    template_name = "delete.html"
    title = _('Delete prescription')
    success_message = _("Prescription deleted.")

    def get_queryset(self):
        return Prescription.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(DeletePrescriptionView,
                        self).get_context_data(*args, **kwargs)
        context['warning'] = _(
            'Are you sure you want to delete the prescription?')
        context['page_title'] = self.title
        context['id'] = Prescription.objects.get(
            id=self.kwargs['pk']).patient.id
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeletePrescriptionView, self).delete(request, *args, **kwargs)


class DashboardChartDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        user = User.objects.get(id=self.kwargs['pk'])
        joined_date = user.date_joined.date()
        delta = date.today() - joined_date
        report_data = []
        for i in range(delta.days + 1):
            data = {}
            report_date = joined_date + timedelta(days=i)
            data['date'] = report_date.strftime('%Y-%m-%d')
            data['count'] = Inhalation.objects.filter(
                device__user=user, inhalation_time__date=report_date).count()
            if DailySurvey.objects.filter(user=user, date=report_date).exists():
                rating = DailySurvey.objects.get(
                    user=user, date=report_date).survey_rating
                if rating is None:
                    rating = 0
            else:
                rating = 0
            data['rating'] = rating
            report_data.append(data)
        print(report_data)
        return Response(report_data, status=HTTP_200_OK)
