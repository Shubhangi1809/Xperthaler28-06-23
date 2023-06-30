from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

app_name = 'api'

urlpatterns = [
    url(r'^login/$', views.Login.as_view(), name = 'login-api'),
    url(r'^register/$', views.Register.as_view(), name = 'register-api'),
    url(r'^get_user_profile/$', views.GetUserProfile.as_view(), name = 'get-profile-details-api'),
    url('update_user_social_links/', views.UpdateUserLinks.as_view(), name = 'update-profile-links-api'),
    url('update_user_profile/', views.UpdateUserProfile.as_view(), name = 'update-profile-details-api'),
    url('get_survay_data/', views.GetSurveyData.as_view(), name = 'get-survay-data-api'),
    url('update_survey_rating/', views.UpdateSurveyRating.as_view(), name = 'update-survay-rating-api'),
    url('get_users_list/', views.GetUsersList.as_view(), name = 'get-users-list-api'),
    url('get_user_data/', views.GetUserData.as_view(), name = 'get-user-data-api'),
    url('save-device/', views.SaveDeviceDetails.as_view(), name = 'save-device'),
    url('save-device-alarm/', views.SaveDeviceAlarms.as_view(), name = 'save-device-alarm'),
    url('save-dose/', views.SaveDose.as_view(), name = 'save-dose'),
]

urlpatterns = format_suffix_patterns(urlpatterns)