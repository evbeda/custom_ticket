from django.conf.urls import url
from django.views.generic import TemplateView
from .views import ViewCreateCustomization
from customizations.views import (
    send_mail_with_ticket_pdf,
    generate_pdf_ticket,
    email_preview_pdf,
    GetEmailTest,
    # UpdateCustomization,
    DeleteCustomization,
    ListCustomization,
    send_mail_test
)

urlpatterns = [

    url(
        r'^$',
        TemplateView.as_view(
            template_name='customizations/menu.html'),
        name='menu'
    ),
    url(
        r'^generate_pdf_ticket/$',
        generate_pdf_ticket,
        name='generate_pdf'
    ),
    url(
        r'^email_preview_pdf/$',
        email_preview_pdf,
        name='email_preview'
    ),
    url(
        r'^send_mail_with_ticket_pdf/$',
        send_mail_with_ticket_pdf,
        name='send_email_with_pdf'
    ),
    url(
        r'^send_mail_test$',
        send_mail_test,
        name='send_mail_test'
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
        TemplateView.as_view(
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
        r'^list/(?P<pk>[0-9]+)/delete$',
        DeleteCustomization.as_view(),
        name='delete_customization'
    ),
    url(r'^list/$',
        ListCustomization.as_view(
            template_name='customizations/list.html'),
        name='list'
        ),

]
