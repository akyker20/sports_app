from django.core.management.base import BaseCommand
from athletes.models import Clip


class Command(BaseCommand):
	help = 'Removes clips - used for testing purposes'

	def handle(self, **options):
		Clip.objects.all().delete()
		print "All clips were removed."