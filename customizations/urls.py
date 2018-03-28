from django.conf.urls import url
from django.views.generic import TemplateView
from customizations.views import send_mail_with_pdf, generate_pdf, PrintPdf


urlpatterns = [
    url(r'^generate-pdf/$', generate_pdf, name='generate_pdf'),
    url(r'^print-pdf/$', PrintPdf.as_view(), name='download_pdf'),
    url(r'^send_mail_with_pdf/$', send_mail_with_pdf, name='send_email_with_pdf'),
    url(r'^sent-mail-success/$', TemplateView.as_view(
        template_name='customizations/successfully_mail.html'), name='successfully_mail'),
    url(r'^create-customization/$', TemplateView.as_view(
        template_name='customizations/create.html'), name='create_customization'),

]
