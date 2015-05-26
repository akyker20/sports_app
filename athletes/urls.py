from django.conf.urls import patterns, include, url

urlpatterns = patterns('',    
    url(r'^$', 'athletes.views.profile', name='athlete_profile'),
    url(r'^register$', 'athletes.views.register', name='athlete_register'),
    url(r'^play_clip$', 'athletes.views.play_clip'),
    url(r'^(?P<athlete_id>\d+)$', 'athletes.views.profile', name='athlete_profile_with_id'),
    url(r'^search', 'athletes.views.search'),
    url(r'^watch_player/(?P<athlete_id>\d+)$', 'athletes.views.watch_player', name='watch_player'),
    url(r'^unwatch_player/(?P<athlete_id>\d+)$', 'athletes.views.unwatch_player', name='unwatch_player'),
    url(r'^comment/$', 'athletes.views.comment'),
    url(r'^star/$', 'athletes.views.star'),
    url(r'^feed/$', 'athletes.views.feed', name='feed'),
    url(r'^top10/$', 'athletes.views.top10', name='top10'),
    url(r'^play_gamefilm$', 'athletes.views.play_gamefilm'),
    url(r'^create_gamefilmclip$', 'athletes.views.create_gamefilmclip'),
    url(r'^delete_gamefilm_clip$', 'athletes.views.delete_gamefilm_clip'),
    url(r'^update_gamefilm_clip$', 'athletes.views.update_gamefilm_clip'),
    url(r'^show_game$', 'athletes.views.show_game'),
    url(r'^get_gamestat$', 'athletes.views.get_gamestat'),
    url(r'^watching$', 'athletes.views.watching', name='watching')
    # url(r'^get_dash_info', 'athletes.views.get_dash_info'),
)