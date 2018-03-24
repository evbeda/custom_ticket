from django.conf.urls import url
from .views import ViewSendEmail


urlpatterns = [
    url(r'^$', ViewSendEmail.as_view(), name='mail'),

]
