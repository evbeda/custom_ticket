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
from customizations.models import Customization
from mail.forms import FormSendEmailPreview
from mail.utils import PDF
from mail.domain import (
    all_data,
    CustomData,
    data_to_dict_all_models
)
from customizations.utils import file_exist, download


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


def get_venue(token, venue_id):
    eventbrite = Eventbrite(token)
    data_venue_json = eventbrite.get('/venues/' + str(venue_id))
    address_1 = data_venue_json['address']['address_1']
    address_2 = data_venue_json['address']['address_2']
    city = data_venue_json['address']['city']
    region = data_venue_json['address']['region']
    country = data_venue_json['address']['country']
    postal_code = data_venue_json['address']['postal_code']
    latitude = data_venue_json['address']['latitude']
    longitude = data_venue_json['address']['longitude']
    return {
        'address_1': address_1,
        'address_2': address_2,
        'city': city,
        'region': region,
        'region': region,
        'country': country,
        'postal_code': postal_code,
        'latitude': latitude,
        'longitude': longitude,
    }


def get_organizer(token, organizer_id):
    eventbrite = Eventbrite(token)
    data_organizer_json = eventbrite.get('/organizers/' + str(organizer_id))
    organizer = data_organizer_json['name']
    return organizer


def get_data(request):
    # token = get_token(request)
    # order = get_order(token, )
    # venue = get_venue(token, )
    # organizer = get_blah(...)
    # process_data(order, venue, organizer)

    print 'Here! get_data'
    print request
    config_data = json.loads(request.body)
    if UserSocialAuth.objects.exists():
        social_user = UserSocialAuth.objects.filter(
            uid=config_data['config']['user_id']
        )
        social_user_id = social_user[0].user_id
        user_request = get_user_model().objects.get(id=social_user_id)

        if Customization.objects.filter(
            user=user_request
        ).exists():
            access_token = social_user[0].extra_data['access_token']
            data = requests.get(
                json.loads(
                    request.body
                )['api_url'] +
                '?token=' +
                access_token +
                '&expand=event,attendees'
            )
            venue = get_venue(
                token=access_token,
                venue_id=data.json()['event']['venue_id']
            )
            organizer = get_organizer(
                token=access_token,
                organizer_id=data.json()['event']['organizer_id']
            )
            return process_data(
                order=data.json(),
                venue=venue,
                organizer=organizer,
                user_id=social_user_id
            )
    return HttpResponse()


def process_data(order, venue, organizer, user_id):
    list_attendee = order['attendees']
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
    customization = Customization.objects.filter(user_id=user_id)
    custom_data = CustomData(
        customization_id=customization[0].id,
        attendees=attendees,
        user_first_name=order['first_name'],
        user_last_name=order['last_name'],
        event_name_text=order['event']['name']['html'],
        from_email=settings.EMAIL_HOST_USER,
        event_start=order['event']['start']['utc'],
        event_venue_location=venue,
        organizer_name=organizer,
        organizer_email='',
        emails=[order['email']],
        order_id=order['id'],
        order_created=order['created'],
        order_status=order['status'],
        is_test=False,
    )
    return do_send_email(custom_data)


def do_send_email(custom_data):

    data = all_data(custom_data)
    if not file_exist(data['logo_path']):
        print 'downloading...'
        if download(data['logo_url'], data['logo_name']):
            print 'downloaded..'
        else:
            print "Unable to download file"
        print 'The file now exist...'
    else:
        print 'file exist...'

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
        # organizer_message = form.cleaned_data['organizer_message']
        # attendee_quantity = form.cleaned_data['attendee_quantity']
        # attendee_question = form.cleaned_data['attendee_question']
        # event_image = form.cleaned_data['event_image']
        attendees = []
        attendee = {
            'attendee_first_name': form.cleaned_data['attendee_first_name'],
            'attendee_last_name': form.cleaned_data['attendee_last_name'],
            'cost_gross': form.cleaned_data['attendee_cost_gross'],
            'barcode': form.cleaned_data['attendee_barcode'],
            'answers': {},
            'ticket_class': form.cleaned_data['ticket_class']
        }

        attendees.append(dict(attendee))
        custom_data = CustomData(
            customization_id=self.kwargs['pk'],
            attendees=attendees,
            organizer_logo=form.cleaned_data['organizer_logo'],
            event_name_text=form.cleaned_data['event_name_text'],
            event_start=form.cleaned_data['event_start'],
            event_venue_location={form.cleaned_data['event_venue_location']},
            organizer_name={form.cleaned_data['organizer_name']},
            organizer_email={form.cleaned_data['organizer_email']},
            #   reserved seating
            user_order_email=form.cleaned_data['user_order_email'],
            order_id='1212',
            order_created=form.cleaned_data['order_created'],
            user_order_first_name=form.cleaned_data['user_order_first_name'],
            user_order_last_name=form.cleaned_data['user_order_last_name'],
            order_status=form.cleaned_data['order_status'],
            # payment_datetime='',
            from_email=form.cleaned_data['from_email'],
            emails=[form.cleaned_data['emails']],
            is_test=True,
        )
        return do_send_email(custom_data)
        # Fixme: double response.
        # return HttpResponseRedirect(reverse('mails:successfully_mail'))
