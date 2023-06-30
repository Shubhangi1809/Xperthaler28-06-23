from ast import Pass
from django import forms
from .models import Appointment, Pharmacy, UserProfile, UserSocialLink, Prescription, UserSettings
from django.contrib.auth.models import User, Group
from django import forms
from xperthaler_backend.constants import GENDER_CHOICES, ROLES
from django.forms import ValidationError
import re
from datetime import date
from django.core.validators import validate_email


class RegistrationAccountTypeForm(forms.ModelForm):
    # groups = Group.objects.all()
    # CHOICES = []
    # for i in groups:
    #     CHOICES.append((i.id, i.name))
    profile_type = forms.ChoiceField(choices=ROLES, widget=forms.RadioSelect)
    class Meta:
        model = UserProfile
        fields = ('profile_type',)


class RegistrationUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm password")
   
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
    def __init__(self, *args, **kwargs):

        super(RegistrationUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['last_name'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['email'].widget.attrs.update({
            'required': True,
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'required': True,
            'class': 'form-control'
        })
        self.fields['confirm_password'].widget.attrs.update({
            'required': True,
            'class': 'form-control'
        })
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name == '' or first_name is None:
            raise ValidationError('This field is required.', code='invalid')
        return first_name
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if last_name == '' or last_name is None:
            raise ValidationError('This field is required.', code='invalid')
        return last_name
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username = email, is_active = True).exists() or User.objects.filter(email = email, is_active = True).exists():
            raise ValidationError('Email address linked to another user', code='invalid')
        return email
    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('Password do not match', code='invalid')
        return password


class FirebaseRegistrationUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm password")
   
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
    def __init__(self, *args, **kwargs):
        super(FirebaseRegistrationUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['last_name'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['email'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
            'readonly': True,
        })
        self.fields['password'].widget.attrs.update({
            'required': True,
            'class': 'form-control'
        })
        self.fields['confirm_password'].widget.attrs.update({
            'required': True,
            'class': 'form-control'
        })
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name == '' or first_name is None:
            raise ValidationError('This field is required.', code='invalid')
        return first_name
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if last_name == '' or last_name is None:
            raise ValidationError('This field is required.', code='invalid')
        return last_name
    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('Password do not match', code='invalid')
        return password

class RegistrationUserProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = UserProfile
        fields = ('dob', 'gender', 'phone_number', 'city', 'state', 'country')

    def __init__(self, *args, **kwargs):
        super(RegistrationUserProfileForm, self).__init__(*args, **kwargs)
        # self.fields['gender'].widget.attrs.update({
        #     'required': True,
        #     'class': 'form-control',
        # })
        self.fields['dob'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['phone_number'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
            'placeholder': '+91XXXXXXXXXX'
        })
        self.fields['city'].widget.attrs.update({
            'required': True,
            'class': 'form-control location',
        })
        self.fields['state'].widget.attrs.update({
            'required': True,
            'class': 'form-control location'
        })
        self.fields['country'].widget.attrs.update({
            'required': True,
            'class': 'form-control location'
        })
    def clean_dob(self):
        dob = self.cleaned_data['dob']
        if dob is None:
            raise ValidationError('This field is required.', code='invalid')
        elif dob > date.today():
            raise ValidationError('Enter a valid date of birth.', code='invalid')
        return dob
    def clean_gender(self):
        gender = self.cleaned_data['gender']
        if gender == '' or gender is None:
            raise ValidationError('This field is required.', code='invalid')
        return gender
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if phone_number == '' or phone_number is None:
            raise ValidationError('This field is required.', code='invalid')
        if not re.match(r'^\+?\d{10,14}$', phone_number):
            raise ValidationError('Invalid phone number.', code='invalid')
        if UserProfile.objects.filter(phone_number = phone_number, user__is_active = True).exists():
            raise ValidationError('Phone number linked to another user', code='invalid')
        return phone_number
    def clean_city(self):
        city = self.cleaned_data['city']
        if city == '' or city is None:
            raise ValidationError('This field is required.', code='invalid')
        return city
    def clean_state(self):
        state = self.cleaned_data['state']
        if state == '' or state is None:
            raise ValidationError('This field is required.', code='invalid')
        return state
    def clean_country(self):
        country = self.cleaned_data['country']
        if country == '' or country is None:
            raise ValidationError('This field is required.', code='invalid')
        return country

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['last_name'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['email'].widget.attrs.update({
            'required': True,
            'class': 'form-control'
        })

class UserProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = UserProfile
        fields = ('dob', 'gender', 'height', 'weight', 'blood_group', 'phone_number', 'city', 'state', 'country', 'notification_status')
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.fields['gender'].widget.attrs.update({
        #     'required': True,
        #     'class': 'form-control',
        # })
        self.fields['dob'].widget.attrs.update({
            'required': True,
            'class': 'form-control',
        })
        self.fields['height'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['weight'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['blood_group'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['phone_number'].widget.attrs.update({
            'required': True,
            'class': 'form-control form-control-lg',
            'placeholder': '+91XXXXXXXXXX'
        })
        self.fields['city'].widget.attrs.update({
            'required': True,
            'class': 'form-control form-control-lg',
        })
        self.fields['state'].widget.attrs.update({
            'required': True,
            'class': 'form-control form-control-lg'
        })
        self.fields['country'].widget.attrs.update({
            'required': True,
            'class': 'form-control form-control-lg'
        })
        self.fields['notification_status'].label = ''
        self.fields['notification_status'].widget.attrs.update({
        })
    def clean_dob(self):
        dob = self.cleaned_data['dob']
        if dob is None:
            raise ValidationError('This field is required.', code='invalid')
        elif dob > date.today():
            raise ValidationError('Enter a valid date of birth.', code='invalid')
        return dob
    def clean_gender(self):
        gender = self.cleaned_data['gender']
        if gender == '' or gender is None:
            raise ValidationError('This field is required.', code='invalid')
        return gender
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if phone_number == '' or phone_number is None:
            raise ValidationError('This field is required.', code='invalid')
        if not re.match(r'^\+?\d{10,14}$', phone_number):
            raise ValidationError('Invalid phone number.', code='invalid')
        return phone_number
    def clean_city(self):
        city = self.cleaned_data['city']
        if city == '' or city is None:
            raise ValidationError('This field is required.', code='invalid')
        return city
    def clean_state(self):
        state = self.cleaned_data['state']
        if state == '' or state is None:
            raise ValidationError('This field is required.', code='invalid')
        return state
    def clean_country(self):
        country = self.cleaned_data['country']
        if country == '' or country is None:
            raise ValidationError('This field is required.', code='invalid')
        return country

class UserSocialLinksForm(forms.ModelForm):
    class Meta:
        model = UserSocialLink
        fields = ('facebook', 'twitter', 'linkedin', 'instagram')

    def __init__(self, *args, **kwargs):
        super(UserSocialLinksForm, self).__init__(*args, **kwargs)
        self.fields['facebook'].widget.attrs.update({
            'class': 'form-control form-control-lg',
        })
        self.fields['twitter'].widget.attrs.update({
            'class': 'form-control form-control-lg'
        })
        self.fields['linkedin'].widget.attrs.update({
            'class': 'form-control form-control-lg'
        })
        self.fields['instagram'].widget.attrs.update({
            'class': 'form-control form-control-lg'
        })

class ProfilePictureForm(forms.ModelForm):
    avatar = forms.ImageField(label='',required=False, error_messages = {'invalid':"Image files only"}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('avatar',)

class AllergiesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('allergies',)
    def __init__(self, *args, **kwargs):
        super(AllergiesForm, self).__init__(*args, **kwargs)
        self.fields['allergies'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'required': False
        })

class AddDoctorForm(forms.Form):
    doctor = forms.CharField(max_length=100, label='Doctor email / id')
    def __init__(self, *args, **kwargs):
        super(AddDoctorForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'required': True
        })
    def clean_doctor(self):
        doctor = self.cleaned_data['doctor']
        valid = False
        if User.objects.filter(username = doctor).exists() and User.objects.get(username = doctor).groups.filter(name='Doctor').exists():
            valid = True
        else:
            try:
                if User.objects.filter(id = int(doctor)).exists() and User.objects.get(id = int(doctor)).groups.filter(name='Doctor').exists():
                    valid = True
            except Exception:
                pass
        if not valid:
            raise ValidationError('Doctor not found.', code='invalid')
        return doctor

class AddCaretakerForm(forms.Form):
    caretaker = forms.CharField(max_length=100, label='Caretaker email / id')
    def __init__(self, *args, **kwargs):
        super(AddCaretakerForm, self).__init__(*args, **kwargs)
        self.fields['caretaker'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'required': True
        })
    def clean_caretaker(self):
        caretaker = self.cleaned_data['caretaker']
        valid = False
        if User.objects.filter(username = caretaker).exists() and User.objects.get(username = caretaker).groups.filter(name='Caretaker').exists():
            valid = True
        else:
            try:
                if User.objects.filter(id = int(caretaker)).exists() and User.objects.get(id = int(caretaker)).groups.filter(name='Caretaker').exists():
                    valid = True
            except Exception:
                pass
        if not valid:
            raise ValidationError('Caretaker not found.', code='invalid')
        return caretaker

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ('name', 'email', 'phone_number')
    def __init__(self, *args, **kwargs):
        super(PharmacyForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
        self.fields['email'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
        self.fields['phone_number'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
            'placeholder': '+91XXXXXXXXXX'
        }
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValidationError('Enter correct email.', code='invalid')
        return email
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+?\d{10,14}$', phone_number):
            raise ValidationError('Invalid phone number.', code='invalid')
        return phone_number

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ('name', 'email', 'phone_number')
    def __init__(self, *args, **kwargs):
        super(EmergencyContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
        self.fields['email'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
        self.fields['phone_number'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
            'placeholder': '+91XXXXXXXXXX'
        }
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValidationError('Enter correct email.', code='invalid')
        return email
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+?\d{10,14}$', phone_number):
            raise ValidationError('Invalid phone number.', code='invalid')
        return phone_number


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('symptoms', 'date', 'time')
    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['symptoms'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
        self.fields['date'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
        self.fields['time'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True,
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ('prescription', )
    def __init__(self, *args, **kwargs):
        super(PrescriptionForm, self).__init__(*args, **kwargs)
        self.fields['prescription'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }
from django.forms.widgets import TextInput
class PreferencesForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ('header_background', 'sidebar_background', 'timings')
    def __init__(self, *args, **kwargs):
        super(PreferencesForm, self).__init__(*args, **kwargs)
        self.fields['header_background'].widget.attrs = {
            'id': 'clr',
            'required': True,
            'type': 'color'
        }
        self.fields['sidebar_background'].widget.attrs = {
            'id': 'sideclr',
            'required': True
        }
        self.fields['timings'].widget.attrs = {
            'class': 'form-control form-control-lg',
            'required': True
        }