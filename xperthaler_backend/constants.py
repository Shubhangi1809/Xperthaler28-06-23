from django.utils.translation import gettext_lazy as _

missing_parameter = _('Parameter missing')

login_success = _('Logged in successfully')

login_failed = _('Incorrect username or password')

incorrect_phone_number = _('Incorrect phone number')

parameter_error = _('Parameter error')

email_exists = _('Email already registered')

username_exists = _('username already registered')

registration_success = _('Registration successful')

incorrect_uid = _('Incorrect user id')

user_not_authenticated = _('User not authenticated')

success_message = _('Successful')

inhalation_saved_message = _('Inhalation saved')

profile_pic_update = _('Profile picture updated')

device_registered = _('Device registered')

device_saved = _('Device saved')

alarm_saved = _('Alarm saved')

no_device_registered = _('No device registered to user')

device_registered_other_user = _('Device already registered to other user')

BLOOD_GROUP_CHOICES = [
    (0, 'A+'),
    (1, 'A-'),
    (2, 'B+'),
    (3, 'B-'),
    (4, 'AB+'),
    (5, 'AB-'),
    (6, 'O+'),
    (7, 'O-'),
    (8, 'Hh'),
]

MEDICINE_TYPE_CHOICES = [
    (0, 'Maintanence Dose'),
    (1, 'Rescue Dose'),
]

STATUS_CHOICES = [
    (0, 'Inactive'),
    (1, 'Active'),
]

BOOLEAN_CHOICES = [
    (0, 'False'),
    (1, 'True'),
]

ALARM_TYPE_CHOICES = [
    ('A', 'Only Buzzer'),
    ('B', 'Only Vibrator'),
    ('C', 'Both Buzzer and Vibrator'),
    ('D', 'No Buzzer No Vibrator'),
]

GENDER_CHOICES = [
    (0, 'Male'),
    (1, 'Female'),
    (2, 'Others'),
]

TIMINGS_TYPE_CHOICES = [
    (0, 'Standard timing'),
    (1, 'Railway timing'),
]

WEATHER_API_URL = 'https://api.weatherapi.com/v1/forecast.json'

ROLES = [
    (3, 'Caretaker'),
    (1, 'Doctor'),
    (2, 'Patient'),
]

USER_CONNECTION_TYPE_CHOICES = [
    (0, 'Doctor'),
    (1, 'Caretaker'),
]

USER_CONNECTION_STATUS_CHOICES = [
    (0, _('Pending')),
    (1, _('Accepted')),
    (2, _('Rejected')),
]

VIEW_STATUS_CHOICES = [
    (0, 'Not Viewed'),
    (1, 'Viewed'),    
    (2, 'Deleted'),  
]
NOTIFICATION_TYPE_CHOICES = [
    (0, 'Doctor add request'),
    (1, 'Caretaker add request'),
]
