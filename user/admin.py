from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Allergies)
admin.site.register(UserProfile)
admin.site.register(UserSocialLink)
admin.site.register(FirebaseAccount)
admin.site.register(UserConnection)
admin.site.register(Pharmacy)
admin.site.register(EmergencyContact)
admin.site.register(Notification)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(UserSettings)