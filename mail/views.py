# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.views.generic import FormView
from django.core.mail import BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from forms import FormEmailSend
from custom_ticket.settings import SERVER_ACCESS_TOKEN
import requests
import json


def get_data(request):
    print "sending email"
    print request.body
    access_token = SERVER_ACCESS_TOKEN
    data = requests.get(
        json.loads(request.body)['api_url'],  + '?token=' + access_token + '&expand=event,attendee'
    )
    name = data.json()['name']
    event = data.json()['event']['name']
    emails = data.json()['email']
    print name + event
    from_email = 'edacticket@gmail.com'
    return do_send_email(name, event, from_email, emails)


def do_send_email(subject, message, from_email, emails):
    logger = logging.getLogger(__name__)
    logger.error('sending email')
    email = EmailMessage(
        subject,
        message,
        from_email,
        emails,
        # ['bcc@example.com'],
        reply_to=['edacticket@gmail.com'],
        headers={'Message-ID': 'foo'},
    )
    # email.attach('design.png', img_data, 'image/png')
    email.attach_file('mail/tickets.png')
    if subject and message and from_email:
        try:
            email.send()
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponse('email sent')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')
