
from survey.models import DailySurvey
from .views import *
from django.urls import path, include, re_path
from django.conf.urls import url
from .views import *

app_name = 'survey'

urlpatterns = [ 
    path('survey', Survey.as_view(), name='survey'),
    path('api/daily_survey/', DailySurveyUpdate.as_view(), name = 'update-daily-survey'),
    path('frontend-weather-forecast/', GetForecast.as_view(), name = 'frontend-weather-forecast'),
    path('calendar-survey-details/', GetSurveyDetails.as_view(), name = 'calendar-survey-details'),
    path('frontend-daily-survey-update/', DailySurveyUpdate.as_view(), name = 'frontend-daily-survey-update'),
    path('frontend-get-daily-rating/', GetDailyRating.as_view(), name = 'frontend-get-daily-rating'),
    path('weather-data', Weather.as_view(), name='weather-data'),
]