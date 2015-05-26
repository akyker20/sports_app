
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<team_id>\d+)$', 'teams.views.team', name='team')

)