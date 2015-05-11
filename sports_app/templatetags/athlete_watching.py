from django import template
from django.template.loader import get_template

register = template.Library()


@register.inclusion_tag('athletes/watching.html')
def athlete_watching(current_athlete, athlete):
	is_watching = False
	if athlete in current_athlete.watching.all():
		is_watching = True
	return {"watching_player": is_watching,
			"athlete_id": athlete.id }