from django.db import models
from django.contrib.auth.models import User
from xperthaler_backend.constants import MEDICINE_TYPE_CHOICES, STATUS_CHOICES, BOOLEAN_CHOICES, ALARM_TYPE_CHOICES

class Device(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    mac_id = models.CharField(max_length=100, null = True, blank = True)
    ble_name = models.CharField(max_length=100, null = True, blank = True)
    company_name = models.CharField(max_length=100, null = True, blank = True)
    medicine_type = models.SmallIntegerField(choices = MEDICINE_TYPE_CHOICES, null = True, blank = True)
    medicine_name = models.CharField(max_length=100, null = True, blank = True)
    max_count = models.IntegerField(null = True, blank = True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(choices = STATUS_CHOICES, null = True, blank = True)
    created = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    updated = models.DateTimeField(auto_now=True, null = True, blank = True)
    class Meta:
        db_table = "device"

    def __str__(self):
        return str(self.user)+':'+str(self.company_name)+':'+str(self.mac_id)

class DeviceAlarm(models.Model):
    device = models.ForeignKey(Device, on_delete = models.CASCADE)
    alarm_1_time = models.TimeField(null = True, blank = True)
    alarm_1_doses = models.SmallIntegerField(null = True, blank = True)
    alarm_1_type = models.CharField(choices = ALARM_TYPE_CHOICES, max_length=10, null = True, blank = True)
    alarm_2_time = models.TimeField(null = True, blank = True)
    alarm_2_doses = models.SmallIntegerField(null = True, blank = True)
    alarm_2_type = models.CharField(choices = ALARM_TYPE_CHOICES, max_length=10, null = True, blank = True)
    alarm_3_time = models.TimeField(null = True, blank = True)
    alarm_3_doses = models.SmallIntegerField(null = True, blank = True)
    alarm_3_type = models.CharField(choices = ALARM_TYPE_CHOICES, max_length=10, null = True, blank = True)
    alarm_4_time = models.TimeField(null = True, blank = True)
    alarm_4_doses = models.SmallIntegerField(null = True, blank = True)
    alarm_4_type = models.CharField(choices = ALARM_TYPE_CHOICES, max_length=10, null = True, blank = True)
    created = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    updated = models.DateTimeField(auto_now=True, null = True, blank = True)
    class Meta:
        db_table = "device_alarm"
    
    def __str__(self):
        return str(self.device)

class Inhalation(models.Model):
    device = models.ForeignKey(Device, on_delete = models.CASCADE)
    location = models.CharField(max_length=100, null = True, blank = True)
    inhalation_time = models.DateTimeField(null = True, blank = True)
    recommended_time = models.DateTimeField(null = True, blank = True)
    x_angle = models.SmallIntegerField(null = True, blank = True)
    y_angle = models.SmallIntegerField(null = True, blank = True)
    shaken = models.SmallIntegerField(choices = BOOLEAN_CHOICES, null = True, blank = True)
    temperature = models.SmallIntegerField(null = True, blank = True)
    count = models.IntegerField(null = True, blank = True)
    created = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    updated = models.DateTimeField(auto_now=True, null = True, blank = True)
    class Meta:
        db_table = "inhaltion"
    
    def __str__(self):
        return str(self.device)+':'+str(self.device.company_name)+':'+str(self.device.mac_id)+':'+str(self.inhalation_time)