from django.conf.urls import patterns, include, url

urlpatterns = patterns('',    
    url(r'^profile$', 'coaches.views.profile', name='coach_profile'),
)