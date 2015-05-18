from django.db import models
from django.db.models import Avg, Sum
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from decimal import Decimal
from polymorphic import PolymorphicModel
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

class CoachProfile(models.Model):
	coach = models.OneToOneField(User)
	date_of_birth = models.DateField()
	current_team = models.OneToOneField(Team, related_name='coach')

	def __unicode__(self):
		return self.coach.get_full_name()

	def save(self, *args, **kwargs):
		""" Before saving add coaches group to user object """
		coaches_group = Group.objects.get(name='coaches')
		self.coach.groups.add(coaches_group)
		super(CoachProfile, self).save(*args, **kwargs)

class AthleteProfile(models.Model):
	athlete = models.OneToOneField(User)
	date_of_birth = models.DateField()
	current_team = models.ForeignKey(Team, related_name='athletes')
	number = models.IntegerField(default=0)
	height = models.IntegerField()
	weight = models.IntegerField()
	vertical_leap = models.IntegerField()
	avg_rebounds = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
	avg_steals = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
	avg_blocks = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
	avg_points = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
	avg_assists = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
	watching = models.ManyToManyField('AthleteProfile', blank=True, null=True, related_name='watched_by')
	
	def __unicode__(self):
		return self.athlete.get_full_name()

	def can_upload_video(self, vid_file_size):
		if self.clip_set.count() == 0:
			return True
		total_space_used = self.clip_set.aggregate(space=Sum('file_size'))['space']
		return total_space_used + vid_file_size < 100000000

	def recomputeAverages(self):
		averages = 	self.gamestat_set.aggregate(points=Avg('points'), 
						rebounds=Avg('rebounds'), assists=Avg('assists'), 
					 	blocks=Avg('blocks'), steals=Avg('steals'))
		self.avg_rebounds = Decimal(averages['rebounds'])
		self.avg_steals = Decimal(averages['steals'])
		self.avg_blocks = Decimal(averages['blocks'])
		self.avg_assists = Decimal(averages['assists'])
		self.avg_points = Decimal(averages['points'])
		self.save()

	def save(self, *args, **kwargs):
		athlete_group = Group.objects.get(name='athletes')
		self.athlete.groups.add(athlete_group)
		super(AthleteProfile, self).save(*args, **kwargs)
		for athlete in self.current_team.athletes.all():
			self.watching.add(athlete)
			athlete.watching.add(self)


class Game(models.Model):
	home_team = models.ForeignKey(Team, related_name="home_games")
	away_team = models.ForeignKey(Team, related_name="away_games")
	home_team_score = models.IntegerField(default=0)
	away_team_score = models.IntegerField(default=0)
	date = models.DateField()

	def __unicode__(self):
		return "{} vs. {} on {}".format(self.home_team, self.away_team, self.date)

	class Meta:
		ordering = ['date']


class GameFilm(models.Model):
	game = models.OneToOneField(Game, related_name='gamefilm')
	coach_uploaded_by = models.ForeignKey(CoachProfile)
	created_at = models.DateTimeField(auto_now_add=True)
	duration = models.IntegerField(default=0)
	file_size = models.IntegerField(default=0)
	mpd_url = models.CharField(max_length=128)

	def __unicode__(self):
		return "Game film of {}".format(self.game)

	def save(self, *args, **kwargs):
		super(GameFilm, self).save(*args, **kwargs)
		if self.game.home_team:
			for athlete in self.game.home_team.athletes.all():
				GameFilmPostedNotification.objects.create(game_film=self, athlete=athlete)
		if self.game.away_team:
			for athlete in self.game.away_team.athletes.all():
				GameFilmPostedNotification.objects.create(game_film=self, athlete=athlete)


class GameStat(models.Model):
	points = models.IntegerField(default=0)
	rebounds = models.IntegerField(default=0)
	assists = models.IntegerField(default=0)
	blocks = models.IntegerField(default=0)
	steals = models.IntegerField(default=0)
	athlete = models.ForeignKey(AthleteProfile)
	created_at = models.DateTimeField(auto_now_add=True)
	game = models.ForeignKey(Game)

	def __unicode__(self):
		return "{}'s stats ({})".format(self.athlete, self.game)

	def compute_value(self):
		return self.points + self.rebounds + self.assists + self.blocks + self.steals

	def save(self, *args, **kwargs):
		if self.athlete.current_team != self.game.home_team and self.athlete.current_team != self.game.away_team:
			raise ValidationError('Player must be from a team that played in the game!')
		else:
			super(GameStat, self).save(*args, **kwargs)
			self.athlete.recomputeAverages()

	class Meta:
		unique_together = ('athlete', 'game',)
		ordering = ['game']


class Clip(PolymorphicModel):
	athlete = models.ForeignKey(AthleteProfile)
	created_at = models.DateTimeField(auto_now_add=True)
	view_count = models.IntegerField(default=0)
	row = models.IntegerField(default=1)
	col = models.IntegerField(default=1)

	def __unicode__(self):
		return "{}'s clip on {}".format(self.athlete, self.created_at)

class UploadedClip(Clip):
	url = models.CharField(max_length=128)
	file_size = models.IntegerField(default=0)
	duration = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)


class GameFilmClip(Clip):
	gamestat = models.ForeignKey(GameStat, related_name='clips')
	game = models.ForeignKey(Game, related_name='clips')
	gamefilm_start_time = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)
	gamefilm_end_time = models.DecimalField(max_digits=6, decimal_places=1, default=0.0)

	def get_gamefilm(self):
		return self.gamestat.game.gamefilm


class Comment(models.Model):
	content = models.TextField(max_length=256)
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(AthleteProfile)

	def __unicode__(self):
		return "Comment by {} on {}".format(self.author, clip)

	class Meta:
		abstract = True

class ClipComment(Comment):
	clip = models.ForeignKey(Clip, related_name='comments')

class GameComment(Comment):
	game = models.ForeignKey(Game, related_name='comments')


class Star(models.Model):
	author = models.ForeignKey(AthleteProfile)
	date = models.DateField(auto_now_add=True)

	class Meta:
		abstract = True

class ClipStar(Star):
	clip = models.ForeignKey(Clip, related_name='stars')

	def __unicode__(self):
		return "Star by {} on clip {}".format(self.author, self.clip)

	class Meta:
		unique_together = ('clip', 'author',)

class GameStatStar(Star):
	gamestat = models.ForeignKey(GameStat, related_name='stars')

	def __unicode__(self):
		return "Star by {} on gamestat {}".format(self.author, self.gamestat)

	class Meta:
		unique_together = ('gamestat', 'author',)


class Notification(PolymorphicModel):
	read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	athlete = models.ForeignKey(AthleteProfile, related_name="notifications")

class GameFilmPostedNotification(Notification):
	game_film = models.ForeignKey(GameFilm)

	def __unicode__(self):
		return "{} posted.".format(self.game_film)
