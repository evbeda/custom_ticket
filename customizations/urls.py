from django.conf.urls import url
from django.views.generic import TemplateView
from customizations.views import (
    DeleteCustomization,
    ViewCreateCustomization,
    update_customization,
)

urlpatterns = [

    url(
        r'^$',
        TemplateView.as_view(
            template_name='customizations/menu.html'),
        name='menu'
    ),
    url(
        r'^create-customization/$',
        ViewCreateCustomization.as_view(),
        name='create_customization'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete$',
        DeleteCustomization.as_view(),
        name='delete_customization'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update$',
        update_customization,
        name='update_customization'
    ),

]
