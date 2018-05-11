from django.conf.urls import url
from django.views.generic import TemplateView
from customizations.views import (
    DeleteBaseTickets,
    DeleteCustomization,
    update_customization,
    update_base_tickets,
    ViewCreateBaseTickets,
    ViewCreateCustomization,
    ViewGenerateBaseTickets,
    ViewListBaseTickets,
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
        r'^error-create$',
        TemplateView.as_view(
            template_name='customizations/error_create.html'),
        name='error_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update$',
        update_customization,
        name='update_customization'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update-baseticket$',
        update_base_tickets,
        name='update_baseticket'
    ),
    url(
        r'^create-baseticket/$',
        ViewCreateBaseTickets.as_view(),
        name='create_baseticket'
    ),
    url(
        r'^generate-baseticket/$',
        ViewGenerateBaseTickets.as_view(),
        name='generate_baseticket'
    ),
    url(
        r'^home-baseticket/$',
        ViewListBaseTickets.as_view(),
        name='home_baseticket'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete-baseticket$',
        DeleteBaseTickets.as_view(),
        name='delete_baseticket'
    ),

]
