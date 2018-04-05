# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from customizations.views import get_pdf_ticket, render_to_string
from django.core.mail import BadHeaderError
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from events.models import CustomEmail
from django.conf import settings
import requests
import json


def get_data(request):
    print "sending email"
    print request.body
    access_token = settings.SERVER_ACCESS_TOKEN
    data = requests.get(
        json.loads(request.body)['api_url'] + '?token=' + access_token + '&expand=event,attendee'
    )
    user_first_name = data.json()['first_name'],
    user_last_name = data.json()['last_name'],
    list_attendee = data.json()['attendees']
    attendees = []
    # for attendee in list_attendee:
    #     attendee_first_name =
    event_name_text = data.json()['event']['name']
    from_email = settings.EMAIL_HOST_USER
    # attendee_first_name = data.json()['attendee']['profile']['first_name']
    # attendee_first_name = data.json()['attendee']['profile']['last_name']
    emails = data.json()['email']
    return do_send_email(

        event_name_text=event_name_text,
        user_order_first_name = user_first_name,
        user_order_last_name = user_last_name,
        from_email=from_email, emails=emails
    )

def get_data_test(request):
    event_name_text = 'EVENTO LALA'
    from_email = settings.EMAIL_HOST_USER
    emails = ['usercticket@gmail.com']
    return do_send_email(event_name_text=event_name_text, from_email=from_email, emails=emails)


def do_send_email(
    #   Attendee : barcode, first name, last name, cost_gross, answers
    attendee=[],
    organizer_logo='',
    event_name_text='',
    event_image='',
    event_start='',
    event_venue_location='',
    #   reserved seating
    user_order_email='',
    #   order_id
    #   order_date
    user_order_first_name='',
    user_order_last_name='',
    payment_status='',
    payment_datetime='',
    ticket_class='',
    from_email='',
    emails=[]
):

    # context data
    data = CustomEmail.data_to_dict(1)
    # body email
    message = render_to_string('customizations/body_mail.html', context=data)
    # compose email
    email = EmailMessage(
        event_name_text,
        message,
        from_email,
        emails,
        reply_to=emails,
        headers={'Message-ID': 'foo'},
    )
    email.content_subtype = 'html'
    pdf = get_pdf_ticket('')

    # attach ticket
    email.attach('ticket', pdf, 'application/pdf')
    try:
        email.send()
        return HttpResponseRedirect(r('customizations:successfully_mail'))
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


# old version
# def do_send_email(subject, message, from_email, emails):
#     logger = logging.getLogger(__name__)
#     logger.error('sending email')
#     email = EmailMessage(
#         subject,
#         message,
#         from_email,
#         emails,
#         # ['bcc@example.com'],
#         reply_to=['edacticket@gmail.com'],
#         headers={'Message-ID': 'foo'},
#     )
#     # email.attach('design.png', img_data, 'image/png')
#     email.attach_file('mail/tickets.png')
#     if subject and message and from_email:
#         try:
#             email.send()
#         except BadHeaderError:
#             return HttpResponse('Invalid header found.')
#         return HttpResponse('email sent')
#     else:
#         # In reality we'd use a form class
#         # to get proper validation errors.
#         return HttpResponse('Make sure all fields are entered and valid.')
