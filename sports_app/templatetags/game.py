from django import template
from django.template.loader import get_template

register = template.Library()


@register.inclusion_tag('athletes/game/game_player_stats.html')
def get_player_stats(game, team):
	stats = game.gamestat_set.filter(game=game, athlete__current_team=team)
	return { "stats":stats, "team_name":team.name }


