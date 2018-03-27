# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.views.generic import FormView
from django.core.mail import BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from forms import FormEmailSend


def send_email(request):
    print "sending email"
    subject = 'test'
    message = 'hello'
    from_email = 'edacticket@gmail.com'
    emails = ['asaiz@eventbrite.com']
    return do_send_email(subject, message, from_email, emails)


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
        return HttpResponseRedirect('/')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')
