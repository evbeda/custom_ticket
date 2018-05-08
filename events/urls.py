from django.conf.urls import url
from events.views import EventsView


urlpatterns = [
    url(r'^$', EventsView.as_view(), name='home_events'),
]
