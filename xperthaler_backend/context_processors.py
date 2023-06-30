from user.models import Notification, UserConnection, UserProfile
from survey.models import SurveyRating
from datetime import date
from django.contrib.contenttypes.models import ContentType

def user_details(request):
    role = 'Anonymous'
    response = {}
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser:
            role = 'admin'
        elif user.is_staff:
            role = 'staff'
        else:
            try:
                if user.groups.filter(name__in = ['Doctor']).exists():
                    role = 'doctor'
                elif user.groups.filter(name__in = ['Patient']).exists():
                    role = 'patient'
                    if SurveyRating.objects.filter(user = user, date = date.today()).exists():
                        rating = SurveyRating.objects.get(user = user, date = date.today()).rating
                    else:
                        rating = 0
                        response['rating'] = rating
                elif user.groups.filter(name__in = ['Caretaker']).exists():
                    role = 'caretaker'
            except Exception:
                role = 'Anonymous'
            response['refresh'] = request.session['refresh']
            notifications = Notification.objects.filter(user = user, delete_status = False).order_by('-id')
            response['notifications'] = notifications
            if Notification.objects.filter(user = user, delete_status = False, view_status = False).exists():
                response['unread_notifications'] = True
            else:
                response['unread_notifications'] = False
    response['role'] = role
    if 'med_type' not in request.session:
        request.session['med_type'] = 0
    response['med_type'] = request.session['med_type']
    return response
