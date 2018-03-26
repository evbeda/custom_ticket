from django.conf.urls import url
from .views import EventsView


urlpatterns = [
    url(r'^$', EventsView.as_view(), name='events'),
]
