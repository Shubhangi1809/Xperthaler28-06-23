from traceback import print_tb
from django.contrib.auth.models import User, Group
from django.db.models.aggregates import Count
from survey.models import DailySurvey, Questions
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .utils import getparameter
from xperthaler_backend import constants
from django.contrib.auth import authenticate
from user.models import FirebaseAccount, UserProfile, UserSocialLink
from survey.models import SurveyRating
from inhaler.models import Device, DeviceAlarm, Inhalation
from datetime import timedelta, datetime, date
from firebase_admin import auth

# API to login
class Login(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            login_type = getparameter(request, 'login_type')
            if int(login_type) not in [0,1]:
                response = {'status': 400, 'message': constants.parameter_error}
                return Response(response, status = HTTP_400_BAD_REQUEST)
            if int(login_type) == 1:
                username = getparameter(request, 'username')
                password = getparameter(request, 'password')
            else:
                phone_number = getparameter(request, 'phone_number')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if int(login_type) == 1:
            user = authenticate(username=username,password=password)
            if user is None:
                response = {'status': 400, 'message': constants.login_failed}
                return Response(response, status = HTTP_400_BAD_REQUEST)
        else:
            if UserProfile.objects.filter(phone_number = phone_number).exists():
                user = UserProfile.objects.get(phone_number = phone_number).user
            else:
                response = {'status': 400, 'message': constants.incorrect_phone_number}
                return Response(response, status = HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user = user)
        response = {'status': 200, 'user_id': user.id, 'auth_token': token.key, 'message': constants.login_success}
        return Response(response, status = HTTP_200_OK)

# API to register
class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            profile_type = getparameter(request, 'profile_type')
            if int(profile_type) == 0 and Group.objects.filter(name = 'Doctor').exists():
                group = Group.objects.get(name = 'Doctor')
            elif int(profile_type) == 1 and Group.objects.filter(name = 'Patient').exists():
                group = Group.objects.get(name = 'Patient')
            elif int(profile_type) == 2 and Group.objects.filter(name = 'Caretaker').exists():
                group = Group.objects.get(name = 'Caretaker')
            else:
                response = {'status': 400, 'message': constants.parameter_error}
                return Response(response, status = HTTP_200_OK)
            full_name = getparameter(request, 'full_name')
            email = getparameter(request, 'email')
            if User.objects.filter(username = email).exists():
                response = {'status' : 400,'message' : constants.email_exists}
                return Response(response, status = HTTP_200_OK)
            gender = getparameter(request, 'gender')
            if int(gender) not in [0, 1, 2]:
                response = {'status': 400, 'message': constants.parameter_error}
                return Response(response, status = HTTP_200_OK)
            password = getparameter(request, 'password')
            country = getparameter(request, 'country')
            state = getparameter(request, 'state')
            city = getparameter(request, 'city')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_200_OK)
        user = User.objects.create(
            username = email,
            first_name = full_name,
            email = email,
        )
        user.set_password(password)
        user.groups.add(group)
        user.save()
        UserProfile.objects.create(
            user = user,
            gender = gender,
            country = country,
            state = state,
            city = city,
        )
        UserSocialLink.objects.create(
            user = user
        )
        token, created = Token.objects.get_or_create(user = user)
        firebase_user = auth.create_user(email = email, password = password, phone_number = '+919845909624')
        FirebaseAccount.objects.get_or_create(uid = firebase_user.uid, user = user)
        response = {'status': 200, 'user_id': user.id, 'auth_token': token.key, 'message': constants.registration_success}
        return Response(response, status = HTTP_200_OK)

# API to get profile details
class GetUserProfile(APIView):
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
            user_profile_obj = UserProfile.objects.get(user = user_obj)
            user_social_obj, created = UserSocialLink.objects.get_or_create(user = user_obj)
            response = {}
            response['name'] = user_obj.first_name
            response['email'] = user_obj.email
            response['gender'] = user_profile_obj.gender
            response['height'] = user_profile_obj.height
            response['weight'] = user_profile_obj.weight
            response['blood_group'] = user_profile_obj.blood_group
            response['phone_number'] = user_profile_obj.phone_number
            response['facebook_url'] = user_social_obj.facebook
            response['twitter_url'] = user_social_obj.twitter
            response['linkedin_url'] = user_social_obj.linkedin
            response['instagram_url'] = user_social_obj.instagram
            response = {'status': 200, 'message': response}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to update profile details
class UpdateUserLinks(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            facebook = request.data.get('facebook', None)
            twitter = request.data.get('twitter', None)
            linkedin = request.data.get('linkedin', None)
            instagram = request.data.get('instagram', None)
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
            user_social_obj, created = UserSocialLink.objects.get_or_create(user = user_obj)
            user_social_obj.facebook = facebook
            user_social_obj.twitter = twitter
            user_social_obj.linkedin = linkedin
            user_social_obj.instagram = instagram
            user_social_obj.save()
            response = {'status': 200, 'message': 'Success'}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to update profile details
class UpdateUserProfile(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            name = request.data.get('name', None)
            email = request.data.get('email', None)
            gender = request.data.get('gender', None)
            height = request.data.get('height', None)
            weight = request.data.get('weight', None)
            blood_group = request.data.get('blood_group', None)
            phone_number = request.data.get('phone_number', None)
            city = request.data.get('city', None)
            state = request.data.get('state', None)
            country = request.data.get('country', None)
            notification_status = request.data.get('notification_status', False)
            if notification_status == 'true':
                notification_status = True
            else:
                notification_status = False
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
            user_obj.first_name = name
            user_obj.email = email
            user_obj.save()
            user_profile_obj = UserProfile.objects.get(user = user_obj)
            user_profile_obj.gender = gender
            user_profile_obj.height = height
            user_profile_obj.weight = weight
            user_profile_obj.blood_group = blood_group
            user_profile_obj.phone_number = phone_number
            user_profile_obj.city = city
            user_profile_obj.state = state
            user_profile_obj.country = country
            user_profile_obj.notification_status = notification_status
            user_profile_obj.save()
            response = {'status': 200}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to get servey responses for ml
class GetSurveyData(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            from_date = request.data.get('from_date', None)
            to_date = request.data.get('to_date', None)
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        questions = Questions.objects.all()
        users = User.objects.all()
        if from_date is None or to_date is None:
            date_range = [datetime.today()]
        else:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d')
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
                date_range = [from_date+timedelta(days=x) for x in range((to_date-from_date).days + 1)]
            except Exception:
                response = {'status': 400, 'message': constants.parameter_error}
                return Response(response, status = HTTP_400_BAD_REQUEST)
        response = {}
        for date in date_range:
            daily_responses = {}
            for user in users:
                daily_surveys = DailySurvey.objects.filter(user = user, date = date)
                user_responses = []
                for question in questions:
                    if daily_surveys.filter(question = question).exists():
                        user_responses.append(daily_surveys.get(question = question).response)
                    else:
                        user_responses.append(0)
                daily_responses[user.id] = user_responses
            if from_date is None or to_date is None:
                response = daily_responses
            else:
                response[date.strftime("%Y-%m-%d")] = daily_responses
        return Response(response, status = HTTP_200_OK)

# API to update survey ratings to database
class UpdateSurveyRating(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            uid = getparameter(request, 'uid')
            rating = getparameter(request, 'rating')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = uid).exists():
            user_obj = User.objects.get(id = uid)
            rating_obj, created = SurveyRating.objects.get_or_create(user = user_obj, date = date.today())
            rating_obj.rating = rating
            rating_obj.save()
            response = {'status': 200, 'message': constants.success_message}
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

# API to get users list for ml
class GetUsersList(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        users = User.objects.all().exclude(is_superuser=True)
        response = {}
        for user in users:
            response[user.id] = {}
            response[user.id]['user_id'] = user.id
            response[user.id]['name'] = user.first_name
            response[user.id]['joined_date'] = user.date_joined.replace(tzinfo=None).strftime("%Y-%m-%d")
        return Response(response, status = HTTP_200_OK)

# API to get data for ml
class GetUserData(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        uid = request.data.get('uid', None)
        only_current_date = request.data.get('only_current_date', 0)
        if uid:
            users = User.objects.filter(id = uid)
        else:
            users = User.objects.all().exclude(is_superuser=True)
        questions = Questions.objects.all()
        response = {}
        current_date = datetime.today().date()
        for user in users:
            daily_surveys = DailySurvey.objects.filter(user = user)
            if int(only_current_date):
                user_created_date = current_date
            else:
                user_created_date = user.date_joined.replace(tzinfo=None).date()
            date = user_created_date
            user_data = {}
            user_data['user_id'] = user.id
            data = {}
            while date <= current_date:
                user_daily_data = {}
                user_responses = []
                for question in questions:
                    if daily_surveys.filter(question = question, date = date).exists():
                        user_responses.append(daily_surveys.get(question = question, date = date).response)
                    else:
                        user_responses.append(0)
                user_daily_data['survey'] = user_responses
                inhalations = []
                inhalation_objects = Inhalation.objects.filter(user = user, inhalation_time__contains = date)
                if inhalation_objects.exists():
                    for i in inhalation_objects:
                        inhalation_data = {}
                        inhalation_data['inhalation_time'] = i.inhalation_time
                        inhalation_data['angle'] = i.angle
                        inhalation_data['shaken'] = i.shaken
                        inhalations.append(inhalation_data)
                user_daily_data['inhalations'] = inhalations
                data[date.strftime("%Y-%m-%d")] = user_daily_data
                date = date+timedelta(days=1)
            response[user.id] = data
        return Response(response, status = HTTP_200_OK)

# API to add/update device details
class SaveDeviceDetails(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user_id = getparameter(request, 'user_id')
            mac_id = getparameter(request, 'mac_id')
            ble_name = request.data.get('ble_name', None)
            company_name = request.data.get('company_name', None)
            medicine_type = request.data.get('medicine_type', None)
            medicine_name = request.data.get('medicine_name', None)
            max_count = request.data.get('max_count', None)
            expiry_date = request.data.get('expiry_date', None)
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        try:
            expiry_date = datetime.strptime(expiry_date, "%d%m%y")
        except Exception:
            response = {'status': 400, 'message': constants.parameter_error}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = user_id).exists():
            user_obj = User.objects.get(id = user_id)
            if medicine_type is not None:
                medicine_type = medicine_type.lower()
                if medicine_type == 'maint' or medicine_type == 'maintenance':
                    medicine_type = 0
                elif medicine_type == 'rescue':
                    medicine_type = 1
                if medicine_type not in [0, 1, None]:
                    response = {'status': 400, 'message': constants.parameter_error}
                    return Response(response, status = HTTP_400_BAD_REQUEST)
            if Device.objects.filter(mac_id = mac_id).exclude(user = user_obj).exists():
                response = {'status': 400, 'message': constants.device_registered_other_user}
                return Response(response, status = HTTP_400_BAD_REQUEST)
            device_obj, created = Device.objects.get_or_create(user = user_obj, mac_id = mac_id)
            if company_name is not None:
                device_obj.company_name = company_name
            if medicine_name is not None:
                device_obj.medicine_name = medicine_name
            if medicine_type is not None:
                device_obj.medicine_type = medicine_type
            if max_count is not None:
                device_obj.max_count = max_count
            if expiry_date is not None:
                device_obj.expiry_date = expiry_date
            if ble_name is not None:
                device_obj.ble_name = ble_name
            device_obj.status = 1
            device_obj.save()
            response = {}
            DeviceAlarm.objects.create(
                device = device_obj
            )
            response['status'] = 200
            response['message'] = constants.device_saved
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)


# API to save device alarms
class SaveDeviceAlarms(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user_id = getparameter(request, 'user_id')
            mac_id = request.data.get('mac_id', None)
            try:
                (alarm_1_time, alarm_1_doses, alarm_1_type) = self.getalarmvalues(request, 'alarm_1')
                (alarm_2_time, alarm_2_doses, alarm_2_type) = self.getalarmvalues(request, 'alarm_2')
                (alarm_3_time, alarm_3_doses, alarm_3_type) = self.getalarmvalues(request, 'alarm_3')
                (alarm_4_time, alarm_4_doses, alarm_4_type) = self.getalarmvalues(request, 'alarm_4')
            except Exception:
                response = {'status': 400, 'message': constants.parameter_error}
                return Response(response, status = HTTP_400_BAD_REQUEST)
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = user_id).exists():
            user_obj = User.objects.get(id = user_id)
            if not Device.objects.filter(user = user_obj).exists():
                response = {'status': 400, 'message': constants.no_device_registered}
                return Response(response, status = HTTP_400_BAD_REQUEST)
            if mac_id is not None and Device.objects.filter(user = user_obj, mac_id = mac_id).exists():
                device = Device.objects.get(user = user_obj, mac_id = mac_id)
            else:
                device = Device.objects.filter(user = user_obj).order_by('-id')[0]
            device_alarm_obj, created = DeviceAlarm.objects.get_or_create(device = device)
            if alarm_1_time is not None:
                device_alarm_obj.alarm_1_time = datetime.strptime(alarm_1_time, "%H%M")
                device_alarm_obj.alarm_1_doses = alarm_1_doses
                device_alarm_obj.alarm_1_type = alarm_1_type
            if alarm_2_time is not None:
                device_alarm_obj.alarm_2_time = datetime.strptime(alarm_2_time, "%H%M")
                device_alarm_obj.alarm_2_doses = alarm_2_doses
                device_alarm_obj.alarm_2_type = alarm_2_type
            if alarm_3_time is not None:
                device_alarm_obj.alarm_3_time = datetime.strptime(alarm_3_time, "%H%M")
                device_alarm_obj.alarm_3_doses = alarm_3_doses
                device_alarm_obj.alarm_3_type = alarm_3_type
            if alarm_4_time is not None:
                device_alarm_obj.alarm_4_time = datetime.strptime(alarm_4_time, "%H%M")
                device_alarm_obj.alarm_4_doses = alarm_4_doses
                device_alarm_obj.alarm_4_type = alarm_4_type
            device_alarm_obj.save()
            response = {}
            response['status'] = 200
            response['message'] = constants.alarm_saved
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

    def getalarmvalues(self, request, val):
        time_name = val + '_time'
        doses_name = val + '_doses'
        type_name = val + '_type'
        alarm_time = request.data.get(time_name, None)
        alarm_doses = request.data.get(doses_name, None)
        alarm_type = request.data.get(type_name, None)
        if alarm_time is None or alarm_doses is None or alarm_type is None or alarm_type not in ['A', 'B', 'C', 'D']:
            return None, None, None
        else:
            return alarm_time, alarm_doses, alarm_type

# API to save inhalations
class SaveDose(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user_id = getparameter(request, 'user_id')
            mac_id = request.data.get('mac_id', None)
            count = getparameter(request, 'count')
            inhalation_time = getparameter(request, 'inhalation_time')
            shaken = getparameter(request, 'shaken')
            x_angle = getparameter(request, 'x_angle')
            y_angle = getparameter(request, 'y_angle')
            temperature = getparameter(request, 'temperature')
            location = request.data.get('location', 'Bangalore')
        except Exception:
            response = {'status': 400, 'message': constants.missing_parameter}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        try:
            inhalation_time = datetime.strptime(inhalation_time, "%H%M%d%m%y")
        except Exception:
            response = {'status': 400, 'message': constants.parameter_error}
            return Response(response, status = HTTP_400_BAD_REQUEST)
        if User.objects.filter(id = user_id).exists():
            user_obj = User.objects.get(id = user_id)
            if not Device.objects.filter(user = user_obj).exists():
                response = {'status': 400, 'message': constants.no_device_registered}
                return Response(response, status = HTTP_400_BAD_REQUEST)
            if mac_id is not None and Device.objects.filter(user = user_obj, mac_id = mac_id).exists():
                device = Device.objects.get(user = user_obj, mac_id = mac_id)
            else:
                device = Device.objects.filter(user = user_obj).order_by('-id')[0]
            if DeviceAlarm.objects.filter(device = device).exists():
                recommended_time = get_recommended_time(device, inhalation_time)
            else:
                recommended_time = None
            Inhalation.objects.create(
                device = device,
                count = count,
                location = location,
                inhalation_time = inhalation_time,
                recommended_time = recommended_time,
                x_angle = x_angle,
                y_angle = y_angle,
                temperature = temperature,
                shaken = shaken,
            )
            response = {}
            response['status'] = 200
            response['message'] = constants.device_registered
            return Response(response, status = HTTP_200_OK)
        else:
            response = {'status': 400, 'message': constants.incorrect_uid}
            return Response(response, status = HTTP_400_BAD_REQUEST)

def get_recommended_time(device, inhalation_time):
    alarms = []
    device_alarms = DeviceAlarm.objects.get(device = device)
    if device_alarms.alarm_1_time:
        alarms.append(get_alarm_datetime(inhalation_time.date(), device_alarms.alarm_1_time, device_alarms.alarm_1_doses))
    if device_alarms.alarm_2_time:
        alarms.append(get_alarm_datetime(inhalation_time.date(), device_alarms.alarm_2_time, device_alarms.alarm_2_doses))
    if device_alarms.alarm_3_time:
        alarms.append(get_alarm_datetime(inhalation_time.date(), device_alarms.alarm_3_time, device_alarms.alarm_3_doses))
    if device_alarms.alarm_4_time:
        alarms.append(get_alarm_datetime(inhalation_time.date(), device_alarms.alarm_4_time, device_alarms.alarm_4_doses))
    alarms = sorted(alarms, key = lambda i: (i['recommended_time']))
    for i in alarms:
        inhalations_count = Inhalation.objects.filter(device = device, recommended_time = i['recommended_time']).count()
        if inhalations_count < i['count']:
            return i['recommended_time']
    return None

def get_alarm_datetime(date, time, doses):
    alarm_datetime = str(date)+str(time)
    alarm_data = {}
    alarm_data['recommended_time'] = datetime.strptime(alarm_datetime, "%Y-%m-%d%H:%M:%S")
    alarm_data['count'] = doses
    return alarm_data