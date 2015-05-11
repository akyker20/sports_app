from django.contrib import admin
from models import AthleteProfile, GameStat, Team, Game, GameFilmClip, UploadedClip

# Register your models here.
admin.site.register(AthleteProfile)
admin.site.register(GameStat)
admin.site.register(Team)
admin.site.register(Game)
admin.site.register(GameFilmClip)
admin.site.register(UploadedClip)