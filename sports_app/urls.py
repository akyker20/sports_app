from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sports_app.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^athletes/', include('athletes.urls')),
    url(r'^coaches/', include('coaches.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^$', 'sports_app.views.home', name='home'),
    url(r'^logout$', 'sports_app.views.logout_user', name='logout'),
    url(r'^login$', 'sports_app.views.login_user', name='login'),

)
