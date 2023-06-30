from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

class UploadExcelForm(forms.Form):
    # user = forms.CharField(label='User', widget=forms.Select())
    # file = forms.FileField(upload_to='documents/')
    file = forms.FileField()