from django import template
from django.template.loader import get_template
from django.core.cache import cache
from athlete.models import AthleteProfile

register = template.Library()


@register.inclusion_tag('athletes/watching.html')
def athlete_watching(current_athlete, athlete):
	is_watching = False
	if athlete in current_athlete.watching.all():
		is_watching = True
	return {"watching_player": is_watching,
			"athlete_id": athlete.id }

@register.filter
def get_watch_suggestions(athlete):
	cache_key = "{}WatchingSuggestions".format(athlete.athlete.username)
	cache_time = 30
	suggestions = cache.get(cache_key)
	if not suggestions:
		athletes_watching = athlete.watching.all()

		""" This dictionary maps an athlete B (that is not watched by the athlete 
			of interest A but is watched by someone that athlete A watches)'s id to the
			number of athletes athlete A watches that watch this athlete B."""
		watching_frequencies = {}
		for athleteB in athletes_watching:
			for athleteC in athleteB.watching.all():
				if athleteC.id in watching_frequencies:
					watching_frequencies[athleteC.id] += 1
				elif athleteC not in athletes_watching:
					watching_frequencies[athleteC.id] = 1
		top_frequencies = sorted(watching_frequencies.items(), key=itemgetter(1), reverse=True)[0:8]
		suggestions = [AthleteProfile.objects.get(id=tup[0]) for tup in top_frequencies]
		cache.set(cache_key, suggestions, cache_time)
	return suggestions