from django.contrib import admin

# Register your models here.
from athletes.models import GameFilm, CoachProfile

# Register your models here.
admin.site.register(GameFilm)
admin.site.register(CoachProfile)