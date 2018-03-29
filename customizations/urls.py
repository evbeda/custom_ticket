from django.conf.urls import url
from django.views.generic import TemplateView
from .views import ViewCreateCustomization
from customizations.views import (
    send_mail_with_pdf,
    generate_pdf,
    PrintPdf,
    email_preview,
    ViewSendPreview,
)

urlpatterns = [

    url(
        r'^$',
        TemplateView.as_view(
            template_name='customizations/menu.html'), name='menu'),
    url(
        r'^generate-pdf/$',
        generate_pdf, name='generate_pdf'),
    url(
        r'^email-preview/$',
        email_preview, name='email_preview'),
    url(
        r'^print-pdf/$',
        PrintPdf.as_view(), name='download_pdf'),
    url(
        r'^send_mail_with_pdf/$',
        send_mail_with_pdf, name='send_email_with_pdf'),
    url(
        r'^sent-mail-success/$',
        TemplateView.as_view(
            template_name='customizations/successfully_mail.html'),
        name='successfully_mail'),
    url(r'^form-send-mail/$',
        ViewSendPreview.as_view(
            template_name='customizations/form_mail.html'),
        name='form_send_mail'),
    url(
        r'^send-mail/$',
        TemplateView.as_view(
            template_name='mail/email_send.html'),
        name='send-mail'),
    url(
        r'^create-customization/$',
        ViewCreateCustomization.as_view(),
        name='create_customization'),
    url(
        r'success',
        ViewCreateCustomization.as_view(),
        name='success_customizations'),

    # url(
    #     r'^view-email/$',
    #     CreateBodyEmail.as_view(),
    #     name='view-email'),
]
