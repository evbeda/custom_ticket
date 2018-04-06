from django.conf.urls import url
from django.views.generic import TemplateView
from .views import ViewCreateCustomization
from customizations.views import (
    GetEmailTest,
    # UpdateCustomization,
    DeleteCustomization,
)

urlpatterns = [

    url(
        r'^$',
        TemplateView.as_view(
            template_name='customizations/menu.html'),
        name='menu'
    ),

    url(
        r'^sent-mail-success/$',
        TemplateView.as_view(
            template_name='customizations/successfully_mail.html'),
        name='successfully_mail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/form_send_mail$',
        GetEmailTest.as_view(
            template_name='customizations/form_mail.html'),
        name='form_send_mail'
    ),
    url(
        r'^send-mail/$',
        GetEmailTest.as_view(
            template_name='mail/email_send.html'),
        name='send-mail'
    ),
    url(
        r'^create-customization/$',
        ViewCreateCustomization.as_view(),
        name='create_customization'
    ),
    url(
        r'success',
        ViewCreateCustomization.as_view(),
        name='success_customizations'
    ),
    # url(
    #     r'^list/(?P<pk>[0-9]+)/update$',
    #     UpdateCustomization.as_view(),
    #     name='update_customization'
    # ),
    url(
        r'^(?P<pk>[0-9]+)/delete$',
        DeleteCustomization.as_view(),
        name='delete_customization'
    ),

]
