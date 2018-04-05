from django.conf.urls import url
from .views import (
    get_data,
    get_data_test,
    send_mail_with_ticket_pdf,
    generate_pdf_ticket,
    email_preview_pdf,
)


urlpatterns = [
    url(r'^mail/', get_data, name='mail'),
    url(r'^test/', get_data_test, name='test'),
    url(
        r'^send_mail_with_ticket_pdf/$',
        send_mail_with_ticket_pdf,
        name='send_email_with_pdf'
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
]
