from django import forms
from .models import DeviceAlarm

class DeviceAlarmsForm(forms.ModelForm):
    class Meta:
        model = DeviceAlarm
        fields = ('alarm_1_time', 'alarm_1_doses', 'alarm_1_type','alarm_2_time', 'alarm_2_doses', 'alarm_2_type',
        'alarm_3_time', 'alarm_3_doses', 'alarm_3_type','alarm_4_time', 'alarm_4_doses', 'alarm_4_type')
    def __init__(self, *args, **kwargs):
        super(DeviceAlarmsForm, self).__init__(*args, **kwargs)
        self.fields['alarm_1_time'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_1_doses'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_1_type'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_2_time'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_2_doses'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_2_type'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_3_time'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_3_doses'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_3_type'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_4_time'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_4_doses'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }
        self.fields['alarm_4_type'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }