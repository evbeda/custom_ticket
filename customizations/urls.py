from django.conf.urls import url
from .views import ViewCreateCustomization


urlpatterns = [
    url(r'^$', ViewCreateCustomization.as_view(), name='customizations'),

]
