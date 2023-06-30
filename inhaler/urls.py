
from survey.models import DailySurvey
from .views import *
from django.urls import path, include, re_path
from django.conf.urls import url
from .views import *

app_name = 'inhaler'

urlpatterns = [ 
    path('calendar-inhalations/', CalendarInhalationList.as_view(), name = 'calendar-inhalations-data'),
    path('frontend-get-reports-data/', GetReportsData.as_view(), name = 'frontend-get-reports-data'),
    path('change-dashboard-dose-type/', changedashboarddosetype, name = 'change-dashboard-dose-type'),
    path('add-data/', adddata, name = 'add-data'),
    path('reports', ReportsView.as_view(), name='reports'),
    path('patient-reports/<pk>', PatientReportsView.as_view(), name='patient-reports'),
    path('devices', DevicesListView.as_view(), name='devices'),
    path('device-alarms/<pk>', DeviceAlarmsView.as_view(), name='device-alarms'),
]