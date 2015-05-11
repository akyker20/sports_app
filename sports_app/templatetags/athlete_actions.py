from django import template
from django.template.loader import get_template

register = template.Library()


@register.inclusion_tag('athletes/star_btns.html')
def athlete_starred(model_instance, user):
	has_starred = True if model_instance.stars.filter(author=user.athleteprofile).exists() else False
	return { "has_starred": has_starred }