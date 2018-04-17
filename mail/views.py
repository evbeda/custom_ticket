# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
from eventbrite import Eventbrite
from django.conf import settings
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import BadHeaderError, EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView
from customizations.models import Customization, UserWebhook

from mail.forms import FormSendEmailPreview
from mail.utils import PDF
from mail.domain import CustomData, all_data, data_to_dict_all_models


def get_pdf_ticket(request, pk):
    data = data_to_dict_all_models(pk)
    pfd_ticket = PDF(
        'tickets/template_default.html',
        [data]
    ).render().getvalue()

    return HttpResponse(pfd_ticket, content_type='application/pdf')


def email_preview_pdf(request, pk):
    data = data_to_dict_all_models(pk)
    return render(request, 'mail/body_mail.html', context=data)


def get_venue(venue_id):
    access_token = settings.SERVER_ACCESS_TOKEN
    eventbrite = Eventbrite(access_token)
    data_venue_json = eventbrite.get('/venues/' + str(venue_id))
    venue = data_venue_json['address']['address_1']
    return {'address_1': venue}


def get_data(request):
    access_token = settings.SERVER_ACCESS_TOKEN
    config_data = json.loads(request.body)
    if UserSocialAuth.objects.exists():
        social_user = UserSocialAuth.objects.filter(
            uid=config_data['config']['user_id']
        )
        user_request = get_user_model().objects.get(id=social_user[0].user_id)

        if Customization.objects.filter(
            user=user_request
        ).exists():
            data = requests.get(
                json.loads(
                    request.body
                )['api_url'] + '?token=' + access_token + '&expand=event,attendees'
            )
            return process_data(data.json())


def process_data(data):
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
    venue_id = data['event']['venue_id']
    custom_data = CustomData(
        customization_id=1,
        attendees=attendees,
        user_first_name=data['first_name'],
        user_last_name=data['last_name'],
        event_name_text=data['event']['name']['html'],
        from_email=settings.EMAIL_HOST_USER,
        event_start=data['event']['start']['utc'],
        event_venue_location=get_venue(str(venue_id)),
        emails=[data['email']],
        order_id=data['id'],
        order_created=data['created'],
        order_status=data['status'],
        is_test=False,
    )
    return do_send_email(custom_data)


def do_send_email(custom_data):

    data = all_data(custom_data)
    message = render_to_string('mail/body_mail.html', context=data)
    email = EmailMessage(
        data['event_name_text'],
        message,
        data['from_email'],
        data['emails'],
        reply_to=data['emails'],
        headers={'Message-ID': 'foo'},
    )
    email.content_subtype = 'html'
    pdf = PDF('tickets/template_default.html', [data]).render().getvalue()
    email.attach('ticket', pdf, 'application/pdf')
    print 'send mail'
    print custom_data.order_id
    print data['emails']
    try:
        email.send()
        if custom_data.is_test:
            return HttpResponseRedirect(r('mails:successfully_mail'))
        else:
            return HttpResponse()

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
        custom_data = CustomData(
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
            attendee_first_name=attendee_first_name,
            attendee_last_name=attendee_last_name,
            barcode=attendee_barcode,
            from_email=from_email,
            emails=emails,
            is_test=True,
        )
        do_send_email(custom_data)
        return HttpResponseRedirect(reverse('mails:successfully_mail'))
