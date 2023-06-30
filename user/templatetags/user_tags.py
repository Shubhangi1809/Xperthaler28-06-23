from traceback import print_tb
from django import template
from user.models import Prescription, UserProfile, UserConnection, UserSettings
from xperthaler_backend.constants import BLOOD_GROUP_CHOICES, GENDER_CHOICES, MEDICINE_TYPE_CHOICES
from datetime import date, timedelta
from django.templatetags.static import static
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from survey.models import DailySurvey

register = template.Library()

@register.filter
def strip_double_quotes(quoted_string):
    return quoted_string.replace('"', '')

@register.filter
def get_blood_group_by_key(key):
    for i, j in BLOOD_GROUP_CHOICES:
        if i == key:
            return j
    return _('Not updated')

@register.filter
def get_user_blood_group(user):
    blood_group = UserProfile.objects.get(user = user).blood_group
    for i, j in BLOOD_GROUP_CHOICES:
        if i == blood_group:
            return j
    return _('Not updated')

@register.filter
def get_gender_by_key(key):
    for i, j in GENDER_CHOICES:
        if i == key:
            return j
    return _('Not updated')

@register.filter
def get_user_gender(user):
    gender = UserProfile.objects.get(user = user).gender
    for i, j in GENDER_CHOICES:
        if i == gender:
            return j
    return _('Not updated')

@register.filter
def get_age_by_dob(dob):
    if dob is None:
        age = 0
    else:
        years = date.today().year - dob.year
        if (date.today() - dob.replace(year=date.today().year)).days >= 0:
            age = years
        else:
            age = years - 1
    return age

@register.filter
def get_avatar_url(user):
    try:
        user_profile_obj = UserProfile.objects.get(user = user)
        url = user_profile_obj.avatar.url
    except Exception:
        url = static('vendors/images/photo1.jpg')
    return url

@register.filter
def get_avatar_thumbnail_url(user):
    try:
        user_profile_obj = UserProfile.objects.get(user = user)
        url = user_profile_obj.avatar_thumbnail.url
    except Exception:
        url = static('vendors/images/photo1.jpg')
    return url

@register.filter
def get_notification_title(notification):
    content_type = notification.content_type
    if notification.type == 0 or notification.type == 1:
        if (content_type.model_class() == UserConnection):
            title = _("New patient request")
    return title

@register.filter
def get_notification_body(notification):
    content_type = notification.content_type
    obj = content_type.get_object_for_this_type(pk=notification.object_id)
    patient_name = obj.user.first_name + ' ' + obj.user.last_name
    if notification.type == 0:
        body = _("{0} has requested to add you as doctor.".format(patient_name))
    elif notification.type == 1:
        body = _("{0} has requested to add you as caretaker.".format(patient_name))
    return body

@register.filter
def get_notification_image(notification):
    content_type = notification.content_type
    obj = content_type.get_object_for_this_type(pk=notification.object_id)
    if (content_type.model_class() == UserConnection):
        notification_user_obj = obj.user
        notification_user_profile_obj = UserProfile.objects.get(user = notification_user_obj)
        try:
            url = notification_user_profile_obj.avatar_thumbnail.url
        except Exception:
            url = static('vendors/images/photo1.jpg')
    return url

@register.filter
def get_user_phone_number(user):
    phone_number = UserProfile.objects.get(user = user).phone_number
    if phone_number is not None:
        return phone_number
    else:
        return _('Not updated')

@register.filter
def get_user_height(user):
    height = UserProfile.objects.get(user = user).height
    if height is not None:
        return height
    else:
        return _('Not updated')
@register.filter

def get_user_weight(user):
    weight = UserProfile.objects.get(user = user).weight
    if weight is not None:
        return weight
    else:
        return _('Not updated')

@register.filter
def get_user_allergy_list(user):
    allergies = UserProfile.objects.get(user = user).allergies.all().order_by('name')
    text = '<ul>'
    for i in allergies:
        text += '<li>' + i.name + '</li>'
    text += '</ul>'
    return mark_safe(text)

@register.filter
def get_user_time_format(time, user):
    if time is None:
        return time
    else:
        if UserSettings.objects.filter(user = user).exists():
            obj = UserSettings.objects.get(user = user)
            if obj.timings:
                return time.strftime('%H:%M')
        return time.strftime('%I:%M %p')

@register.filter
def get_user_datetime_format(datetime, user):
    if datetime is None:
        return datetime
    else:
        if UserSettings.objects.filter(user = user).exists():
            obj = UserSettings.objects.get(user = user)
            if obj.timings:
                return datetime.strftime('%d-%m-%Y %H:%M')
        return datetime.strftime('%d-%m-%Y %I:%M %p')

@register.filter
def get_last_prescription(patient, doctor):
    if Prescription.objects.filter(doctor = doctor, patient = patient).exists():
        prescription = Prescription.objects.filter(doctor = doctor, patient = patient).order_by('-id')[0]
        return prescription.prescription
    else:
        return _('No history')

@register.filter
def get_type_of_medication(type):
    for i, j in MEDICINE_TYPE_CHOICES:
        if i == int(type):
            return j
    return _("Incorrect value")

@register.filter
def get_deviation_time(inhalation_time, recommended_time):
    deviation = None
    if inhalation_time is not None and recommended_time is not None:
        if inhalation_time > recommended_time:
            deviation = inhalation_time - recommended_time
        else:
            deviation = recommended_time - inhalation_time
    return deviation

@register.filter
def get_survey_rating(user, inhalation_time):
    survey_rating = 'No rating'
    if DailySurvey.objects.filter(user = user, date = inhalation_time.date()).exists():
        survey = DailySurvey.objects.get(user = user, date = inhalation_time.date())
        survey_rating = survey.survey_rating
    return survey_rating