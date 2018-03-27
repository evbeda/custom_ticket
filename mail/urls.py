from django.conf.urls import url
from .views import send_email


urlpatterns = [
    url(r'^$', send_email, name='mail'),

]
