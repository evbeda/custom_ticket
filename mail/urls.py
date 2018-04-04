from django.conf.urls import url
from .views import get_data


urlpatterns = [
    url(r'^$', get_data, name='mail'),

]
