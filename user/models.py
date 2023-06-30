from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.validators import validate_email
from xperthaler_backend.constants import (BLOOD_GROUP_CHOICES, GENDER_CHOICES, TIMINGS_TYPE_CHOICES,
USER_CONNECTION_TYPE_CHOICES, USER_CONNECTION_STATUS_CHOICES, VIEW_STATUS_CHOICES, NOTIFICATION_TYPE_CHOICES)
from xperthaler_backend.utils import pictureoriginalname, picturethumbnailname
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, SmartResize
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create(user = instance)
        UserSettings.objects.create(user = instance)

class Allergies(models.Model):
    key = models.CharField(max_length=100, null = True, blank = True)
    name = models.CharField(max_length=100, null = True, blank = True)
    class Meta:  
        db_table = "allergies"
    
    def __str__(self):
        return str(self.name)

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    gender = models.SmallIntegerField(choices = GENDER_CHOICES, null = True, blank = True)
    height = models.CharField(max_length=10, null = True, blank = True)
    weight = models.CharField(max_length=10, null = True, blank = True)
    blood_group = models.SmallIntegerField(choices = BLOOD_GROUP_CHOICES, null = True, blank = True)
    phone_number = models.CharField(max_length=20, null = True, blank = True)
    country = models.CharField(max_length=150, null = True, blank = True)
    city = models.CharField(max_length=150, null = True, blank = True)
    state = models.CharField(max_length=150, null = True, blank = True)
    notification_status = models.BooleanField(default=False)
    allergies = models.ManyToManyField(Allergies, blank=True)
    avatar = ProcessedImageField(upload_to=pictureoriginalname, format='JPEG', processors=[ResizeToFill(500, 500)], options={'quality': 100}, null = True, blank = True)
    avatar_thumbnail = ProcessedImageField(upload_to=picturethumbnailname, format='JPEG', processors=[ResizeToFill(250, 250)], options={'quality': 100}, null = True, blank = True)
    dob = models.DateField(verbose_name="Date of birth", null=True,blank=True)
    class Meta:  
        db_table = "user_profile"
    
    def __str__(self):
        return str(self.user)

class UserSocialLink(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    facebook = models.CharField(max_length=100, null = True, blank = True)
    twitter = models.CharField(max_length=100, null = True, blank = True)
    linkedin = models.CharField(max_length=100, null = True, blank = True)
    instagram = models.CharField(max_length=100, null = True, blank = True)
    class Meta:  
        db_table = "user_social_links"
    
    def __str__(self):
        return str(self.user)

class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    header_background = models.CharField(max_length=100, null = True, blank = True, default='#ffffff')
    sidebar_background = models.CharField(max_length=100, null = True, blank = True, default='#d97d54')
    timings = models.SmallIntegerField(choices = TIMINGS_TYPE_CHOICES, null = True, blank = True, default=0)
    class Meta:  
        db_table = "user_settings"
    
    def __str__(self):
        return str(self.user)

class FirebaseAccount(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    uid = models.CharField(max_length=100, null = True, blank = True)
    class Meta:  
        db_table = "firebase_account"
    
    def __str__(self):
        return str(self.user.username)

class Pharmacy(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(max_length=100, null = True, blank = True)
    email = models.CharField(max_length=100, null = True, blank = True)
    phone_number = models.CharField(max_length=20, null = True, blank = True)
    class Meta:  
        db_table = "pharmacies"
    
    def __str__(self):
        return str(self.user)

class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    name = models.CharField(max_length=100, null = True, blank = True)
    email = models.CharField(max_length=100, null = True, blank = True)
    phone_number = models.CharField(max_length=20, null = True, blank = True)
    class Meta:  
        db_table = "emergency_contacts"
    
    def __str__(self):
        return str(self.user)

class UserConnection(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    connection = models.ForeignKey(User, related_name='connection', on_delete = models.CASCADE, null = True, blank = True)
    type = models.SmallIntegerField(choices = USER_CONNECTION_TYPE_CHOICES, null = True, blank = True)
    status = models.SmallIntegerField(choices = USER_CONNECTION_STATUS_CHOICES, null = True, blank = True)
    class Meta:  
        db_table = "user_connections"
    
    def __str__(self):
        return str(self.user)

class Notification(models.Model):
    message_id = models.CharField(max_length= 200, blank=True, null= True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notified_user")
    view_status = models.BooleanField(default=False)
    delete_status = models.BooleanField(default=False)
    # expiry_date = models.DateField(null=True,blank=True)
    type = models.SmallIntegerField(choices = NOTIFICATION_TYPE_CHOICES)
    notification_date = models.DateTimeField(auto_now_add=True)
    content_type =   models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object=GenericForeignKey('content_type', 'object_id')
   
    class Meta:
        db_table = "notifications"
        
    def __str__(self):
        return str(self.user)

class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name='patient', on_delete = models.CASCADE)
    doctor = models.ForeignKey(User, related_name='doctor', on_delete = models.CASCADE, null = True, blank = True)
    symptoms = models.CharField(max_length=512, null = True, blank = True)
    date = models.DateField(null=True,blank=True)
    time = models.TimeField(null=True,blank=True)
    class Meta:  
        db_table = "appointments"
    
    def __str__(self):
        return str(self.patient)

class Prescription(models.Model):
    patient = models.ForeignKey(User, related_name='prescribing_doctor', on_delete = models.CASCADE)
    doctor = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    prescription = models.CharField(max_length=512, null = True, blank = True)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:  
        db_table = "prescriptions"
    
    def __str__(self):
        return str(self.prescription)