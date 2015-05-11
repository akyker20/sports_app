from django.shortcuts import render
from sports_app.decorators import group_required
from athletes.models import GameFilm
from django.views.decorators.csrf import csrf_exempt
import json, datetime
from django.http import HttpResponse, HttpResponseForbidden

from athletes.models import Game


@group_required('coaches')
def profile(request, athlete_id=None):
	coach = request.user.coachprofile
	return render(request, 'coaches/profile.html', {"coach":coach})
