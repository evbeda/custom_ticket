from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from .views import IndexView
from events.views import HomeView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'events/', include('events.urls')),
    url(r'mail/', include('mail.urls')),
    url(r'customizations/', include('customizations.urls')),
    url('', include('social_django.urls', namespace='social')),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^password_reset/$', login, name='password_reset'),
    url(r'^home/', HomeView.as_view()),
]
