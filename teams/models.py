from django.db import models
from operator import attrgetter
from itertools import chain


class Team(models.Model):
	city = models.CharField(max_length=24)
	state = models.CharField(max_length=16)
	name = models.CharField(max_length=32)

	def get_games(self):
		return sorted(chain(self.home_games.all(), self.away_games.all()),
			key=attrgetter('date'), reverse=True)

	def __unicode__(self):
		return self.name