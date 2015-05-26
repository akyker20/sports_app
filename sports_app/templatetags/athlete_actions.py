from django import template
from django.template.loader import get_template
from athletes.models import SharedClip

register = template.Library()


@register.inclusion_tag('athletes/star_btns.html')
def athlete_starred(model_instance, user):
	has_starred = model_instance.stars.filter(author=user.athleteprofile).exists()
	return { "has_starred": has_starred }


@register.inclusion_tag('athletes/share_btns.html')
def athlete_shared(model_instance, user):
	athlete = user.athleteprofile
	has_shared = SharedClip.objects.filter(sharing_athlete=athlete, clip=model_instance).exists()
	return { "has_shared": has_shared }