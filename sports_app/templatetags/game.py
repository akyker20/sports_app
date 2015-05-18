from django import template
from django.template.loader import get_template

register = template.Library()


@register.inclusion_tag('athletes/game/game_player_stats.html')
def get_player_stats(game, team):
	stats = game.gamestat_set.filter(game=game, athlete__current_team=team)
	return { "stats":stats, "team_name":team.name }


@register.assignment_tag
def get_games_best_player(game, team):
	gamestats = game.gamestat_set.filter(athlete__current_team=team)
	largest_val, best_gamestat = -1, None
	for stat in gamestats:
		stat_val = stat.compute_value()
		if stat_val > largest_val:
			largest_val, best_gamestat = stat_val, stat
	return best_gamestat





