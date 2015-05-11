from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.extras.widgets import SelectDateWidget

class AuthenticateForm(AuthenticationForm):
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'password'}))

class AthleteCreationForm(UserCreationForm):
	dob =  forms.DateField(widget=SelectDateWidget())