from django.db import models
from teams.models import Team
from django.contrib.auth.models import User, Group

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