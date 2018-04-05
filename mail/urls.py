from django.conf.urls import url
from .views import get_data, get_data_test


urlpatterns = [
    url(r'^mail/', get_data, name='mail'),
    url(r'^test/', get_data_test, name='test'),

]
