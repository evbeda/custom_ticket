from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login, logout

from customizations.views import ListCustomizations


urlpatterns = [
    url(
        r'^admin/',
        admin.site.urls
    ),
    url(
        r'^$',
        ListCustomizations.as_view(),
        name='list_customizations'
    ),
    url(
        r'customizations/',
        include(
            'customizations.urls',
            namespace='customizations'
        )
    ),
    url(
        r'events/',
        include('events.urls',
                namespace='events')
    ),
    url(
        r'mail/',
        include('mail.urls',
                namespace='mails')
    ),
    url(
        '',
        include('social_django.urls', namespace='social')
    ),
    url(
        r'^accounts/login/$',
        login, name='login'
    ),
    url(
        r'^accounts/logout/$',
        logout, {'next_page': '/events/'},
        name='logout'
    ),
    url(
        r'^password_reset/$',
        login,
        name='password_reset'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
