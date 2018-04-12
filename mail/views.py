# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import requests
import json
from eventbrite import Eventbrite
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import BadHeaderError, EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView

from mail.forms import FormSendEmailPreview
from mail.domain import data_to_dict_all_models
from mail.utils import PDF


def get_pdf_ticket(request, pk):
    data = data_to_dict_all_models(pk)
    pfd_ticket = PDF(
        'tickets/template_default.html',
        [data]
    ).render().getvalue()
    return HttpResponse(pfd_ticket, content_type='application/pdf')


def get_pdf_ticket_do_send_mail(request, pk):
    data = data_to_dict_all_models(pk)
    return PDF('tickets/template_default.html', [data]).render().getvalue()


def email_preview_pdf(request, pk):
    data = data_to_dict_all_models(pk)
    return render(request, 'mail/body_mail.html', context=data)


def get_venue(venue_id):
    access_token = settings.SERVER_ACCESS_TOKEN
    eventbrite = Eventbrite(access_token)
    # import ipdb; ipdb.set_trace()
    data_venue_json = eventbrite.get('/venues/' + str(venue_id))
    data_venue = json.loads(data_venue_json)
    venue = data_venue['address']['address_1']

    return venue


def get_data(request):
    print "sending email"
    print request.body
    access_token = settings.SERVER_ACCESS_TOKEN
    data = requests.get(
        json.loads(
            request.body
        )['api_url'] + '?token=' + access_token + '&expand=event,attendees'
    )
    return process_data(data.json())


def process_data(data):
    user_first_name = data['first_name'],
    user_last_name = data['last_name'],
    list_attendee = data['attendees']

    attendees = []
    for att in list_attendee:
        attendee = {
            'attendee_first_name': att['profile']['first_name'],
            'attendee_last_name': att['profile']['last_name'],
            'cost_gross': att['costs']['gross']['value'],
            'barcode': att['barcodes'][0]['barcode'],
            'answers': att['answers'],
            'ticket_class': att['ticket_class_name']
        }
        attendees.append(dict(attendee))
    event_name_text = data['event']['name']['html']
    from_email = settings.EMAIL_HOST_USER
    event_start = data['event']['start']['utc']
    venue_id = data['event']['venue_id']
    venue = get_venue(venue_id)
    emails = data['email']
    order_id = data['id']
    order_created = data['created']
    order_status = data['status']

    return do_send_email(
        attendees=attendees,
        event_name_text=event_name_text,
        user_order_first_name=user_first_name,
        user_order_last_name=user_last_name,
        event_start=event_start,
        order_id=order_id,
        order_created=order_created,
        order_status=order_status,
        event_venue_location=venue,
        from_email=from_email,
        emails=[emails]
    )


def data_to_dict_all(customization_id, data_api):
    data_model = data_to_dict_all_models(customization_id)
    data = dict(list(data_model.items()) + list(data_api.items()))
    return data


def do_send_email(
    customization_id=int(1),
    attendees=[],
    organizer_logo='',
    event_name_text='',
    event_start='',
    event_venue_location={},
    #   reserved seating
    user_order_email='',
    order_id='',
    order_created='',
    user_order_first_name='',
    user_order_last_name='',
    order_status='',
    # payment_datetime='',
    ticket_class='',
    from_email='',
    emails=[],

):
    data_api = ({
        'customization_id': customization_id,
        'attendees': attendees,
        'attendee_first_name': attendees[0]['attendee_first_name'],
        'event_venue_location': event_venue_location,
        'event_name_text': event_name_text,
        'event_start': event_start,
        #   reserved seating
        # organizer_name
        'user_order_email': user_order_email,
        'order_id': order_id,
        'organizer_logo': organizer_logo,
        'order_created': order_created,
        'user_order_first_name': user_order_first_name,
        'user_order_last_name': user_order_last_name,
        'order_status': order_status,
        # payment_datetime:'',
        'ticket_class': ticket_class,
        'from_email': from_email,
        'emails': emails,
        'event_venue_location_name': 'Wall Street 1234',
        'barcode': attendees[0]['barcode'],
    })
    data = data_to_dict_all(customization_id, data_api)
    message = render_to_string('mail/body_mail.html', context=data)
    email = EmailMessage(
        event_name_text,
        message,
        from_email,
        emails,
        reply_to=emails,
        headers={'Message-ID': 'foo'},
    )
    email.content_subtype = 'html'
    pdf = PDF('tickets/template_default.html', [data]).render().getvalue()
    email.attach('ticket', pdf, 'application/pdf')
    try:
        email.send()
        return HttpResponseRedirect(r('mails:successfully_mail'))
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


class GetEmailTest(LoginRequiredMixin, FormView):
    form_class = FormSendEmailPreview
    template_name = 'mail/form_mail.html'

    def form_valid(self, form):
        print form.cleaned_data
        attendee_barcode = form.cleaned_data['attendee_barcode']
        attendee_first_name = form.cleaned_data['attendee_first_name']
        attendee_last_name = form.cleaned_data['attendee_last_name']
        organizer_message = form.cleaned_data['organizer_message']
        organizer_logo = form.cleaned_data['organizer_logo']
        attendee_cost_gross = form.cleaned_data['attendee_cost_gross']
        attendee_quantity = form.cleaned_data['attendee_quantity']
        attendee_question = form.cleaned_data['attendee_question']
        order_status = form.cleaned_data['order_status']
        order_created = form.cleaned_data['order_created']
        ticket_class = form.cleaned_data['ticket_class']
        event_name_text = form.cleaned_data['event_name_text']
        event_image = form.cleaned_data['event_image']
        event_start = form.cleaned_data['event_start']
        event_venue_location = form.cleaned_data['event_venue_location']
        user_order_email = form.cleaned_data['user_order_email']
        user_order_first_name = form.cleaned_data['user_order_first_name']
        user_order_last_name = form.cleaned_data['user_order_last_name']
        from_email = form.cleaned_data['from_email']
        emails = [form.cleaned_data['emails']]
        attendees = []
        attendee = {
            'attendee_first_name': attendee_first_name,
            'attendee_last_name': attendee_last_name,
            'cost_gross': attendee_cost_gross,
            'barcode': attendee_barcode,
            'answers': {},
            'ticket_class': ticket_class
        }

        attendees.append(dict(attendee))
        do_send_email(
            customization_id=self.kwargs['pk'],
            attendees=attendees,
            organizer_logo=organizer_logo,
            event_name_text=event_name_text,
            event_start=event_start,
            event_venue_location={event_venue_location},
            #   reserved seating
            user_order_email=user_order_email,
            order_id='1212',
            order_created=order_created,
            user_order_first_name=user_order_first_name,
            user_order_last_name=user_order_last_name,
            order_status=order_status,
            # payment_datetime='',
            ticket_class=ticket_class,
            from_email=from_email,
            emails=emails
        )
        return HttpResponseRedirect(reverse('mails:successfully_mail'))
