# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import BadHeaderError, EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.views.generic import FormView
from .forms import FormSendEmailPreview
from events.models import CustomEmail, TicketType
from mail.utils import PDF
import json
import requests


def get_pdf_ticket(self):
    data = TicketType.data_to_dict(1)
    return PDF('tickets/template_default.html', [data]).render().getvalue()


def generate_pdf_ticket(request):
    ticket_pdf = get_pdf_ticket(request)
    return HttpResponse(ticket_pdf, content_type='application/pdf')


def get_pdf_body_email(request):
    data = CustomEmail.data_to_dict(1)
    return PDF('mail/body_mail.html', [data]).render().getvalue()


def email_preview_pdf(request):
    email_pdf = get_pdf_body_email(request)
    return HttpResponse(email_pdf, content_type='application/pdf')

# not use for testing - use do_send_email in mail/views.py


def send_mail_with_ticket_pdf(request):
    data = CustomEmail.data_to_dict(1)
    content = render_to_string('mail/body_mail.html', context=data)
    content = mark_safe(content)
    email = EmailMessage(
        'Test Send Ticket',
        content,
        'edacticket@gmail.com',
        ['usercticket@gmail.com']
    )
    email.content_subtype = 'html'
    pdf = get_pdf_ticket(request)
    email.attach('ticket', pdf, 'application/pdf')
    email.send()
    return HttpResponseRedirect(r('mails:successfully_mail'))


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
        user_order_first_name=user_first_name,
        user_order_last_name=user_last_name,
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
    message = render_to_string('mail/body_mail.html', context=data)
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
        return HttpResponseRedirect(r('mails:successfully_mail'))
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


class GetEmailTest(LoginRequiredMixin, FormView):
    form_class = FormSendEmailPreview
    template_name = 'mail/form_mail.html'
    success_url = 'form_mail.html'

    def post_email(self, request, *args, **kwargs):
        is_form_valid = super(GetEmailTest, self).post(request, *args, **kwargs)
        if is_form_valid:
            email_send = request.POST.get('email_send')
            return email_send

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
