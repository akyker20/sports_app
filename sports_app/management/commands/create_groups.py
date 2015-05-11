from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	help = 'Creates athletes and coaches group'

	def handle(self, **options):
		if Group.objects.count() == 0:
			Group.objects.create(name='athletes')
			Group.objects.create(name='coaches')
			print "Athlete and Coach groups successfully created."
		else:
			print "Groups already exist. Remove them to run this command."