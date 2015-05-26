from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from athletes.models import Team

@login_required
def team(request, team_id):
	team = Team.objects.get(id=int(team_id))
	recent_games = team.get_games()
	context = { "team":team, "recent_games":recent_games }
	if hasattr(request.user, 'athleteprofile'):
		context["athlete"] = request.user.athleteprofile

	return render(request, 'teams/team.html', context)
