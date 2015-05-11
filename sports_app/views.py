from django.shortcuts import render
from sports_app.forms import AuthenticateForm, AthleteCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import date
from sports_app.decorators import group_required



def home(request):
  return render(request, 'home.html', {})


# Create your views here.
def login_user(request):
	form = AuthenticateForm()
	if request.method == 'POST':
		form = AuthenticateForm(data=request.POST)
		if form.is_valid():
			login(request, form.get_user())
			if form.get_user().groups.filter(name='athletes').exists():
				return redirect('athlete_profile')
			elif form.get_user().groups.filter(name='coaches').exists():
				return redirect('coach_profile')
	return redirect('home')


@login_required
def logout_user(request):
  logout(request)
  return redirect('home')

