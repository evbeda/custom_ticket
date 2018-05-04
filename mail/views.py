# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
import threading
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
from django.views.generic import FormView
from mail.forms import FormSendEmailPreview
import datetime
import time
from mail.utils import (
    PDF,
)
from mail.domain import (
    all_data,
    CustomData,
    data_to_dict_all_models,
    data_fake
)
# from customizations.utils import file_exist, download
from django.shortcuts import render, get_object_or_404, redirect
from customizations.utils import process_logo
from customizations.models import (
    Customization,
    TicketSequence)


def get_pdf_ticket(request, pk):
    data = data_fake(pk)
    customization = get_object_or_404(Customization, pk=pk)
    html_url = customization.ticket_template.select_design_template.template_source
    pdf = PDF(html_url, [data]).render().getvalue()
    return HttpResponse(pdf, content_type='application/pdf')


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


def webhook_available_to_process(user_id):
    if UserSocialAuth.objects.exists():
        if social_user_exists(user_id):
            social_user_id = get_social_user_id(user_id)
            user_request = get_user_model().objects.get(id=social_user_id)
            if Customization.objects.filter(
                user=user_request
            ).exists():
                return True
    return False


def social_user_exists(user_id):
    social_user = UserSocialAuth.objects.filter(
        uid=user_id
    )
    if len(social_user) == 0:
        return False
    else:
        return True


def get_social_user_id(user_id):
    social_user = get_social_user(user_id)
    return social_user.user_id


def get_social_user(user_id):
    social_user = UserSocialAuth.objects.filter(
        uid=user_id
    )
    return social_user[0]


def accept_webhook(request):
    print 'Here! accepting webhook'
    threading.Thread(target=get_data, args=(request.body,)).start()
    print "responding webhook"
    return HttpResponse()


def get_data(body):
    print 'Here! get_data'
    print body
    config_data = json.loads(body)
    user_id = config_data['config']['user_id']
    if webhook_available_to_process(user_id):
        social_user = get_social_user(user_id)
        access_token = social_user.extra_data['access_token']
        data = requests.get(
            json.loads(
                body
            )['api_url'] +
            '?token=' +
            access_token +
            '&expand=event,attendees.reserved_seating'
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
            user_id=get_social_user_id(user_id)
        )
    return HttpResponse()


def register_ticket(attendee, customization):

    event_sequence = TicketSequence.objects.filter(
        event_id=attendee['event_id']
    ).count()

    ticket_type_sequence = TicketSequence.objects.filter(
        ticket_type_id=attendee['ticket_class_id']
    ).count()

    TicketSequence.objects.create(
        event_id=attendee['event_id'],
        ticket_type_id=attendee['ticket_class_id'],
        barcode=str(attendee['barcode']),
        event_sequence=event_sequence + 1,
        ticket_type_sequence=ticket_type_sequence + 1,
        customization=customization,
    )


def get_event_sequence(barcode):
    event_sequence = TicketSequence.objects.get(
        barcode=barcode
    ).event_sequence

    return {
        'event_sequence': event_sequence,
    }


def get_ticket_type_sequence(barcode):

    ticket_type_sequence = TicketSequence.objects.get(
        barcode=barcode
    ).ticket_type_sequence

    return {
        'ticket_type_sequence': ticket_type_sequence,
    }


def process_data(order, venue, organizer, user_id):
    list_attendee = order['attendees']
    customization = Customization.objects.select_related(
        'ticket_template'
    ).get(user_id=user_id)
    template_url = customization.ticket_template.select_design_template.template_source
    attendees = []
    for att in list_attendee:
        if att['reserved_seating'] is None:
            reserved_seating = None
        else:
            reserved_seating = att['reserved_seating']['description']
        attendee = {
            'attendee_first_name': att['profile']['first_name'],
            'attendee_last_name': att['profile']['last_name'],
            'cost_gross': att['costs']['gross']['display'],
            'barcode': att['barcodes'][0]['barcode'],
            'answers': att['answers'],
            'ticket_class': att['ticket_class_name'],
            'ticket_class_id': att['ticket_class_id'],
            'event_id': att['event_id'],
            'reserved_seating': reserved_seating,
        }
        register_ticket(attendee, customization)
        attendees.append(dict(attendee))

    date_start = datetime.datetime(
        *time.strptime(order['event']['start']['local'],
                       "%Y-%m-%dT%H:%M:%S")[:6]
    )
    format_date_start = date_start.strftime("%d/%m/%y %I:%M%p")
    ticket_template = customization.ticket_template
    custom_data = CustomData(
        customization=customization,
        attendees=attendees,
        user_first_name=order['first_name'],
        user_last_name=order['last_name'],
        event_name_text=order['event']['name']['html'],
        from_email=settings.EMAIL_HOST_USER,
        event_start=format_date_start,
        event_venue_location=venue,
        organizer_name=organizer,
        organizer_email='',
        emails=[order['email']],
        order_id=order['id'],
        order_created=order['created'],
        order_status=order['status'],
        is_test=False,
        footer_description=ticket_template.footer_description,
        template_url=template_url,
    )
    return do_send_email(custom_data)


def get_url(attendee):
    url = attendee['url']
    return url


def do_send_email(custom_data):
    data = all_data(custom_data)
    process_logo(data['logo_path'], data['logo_url'], data['logo_name'])
    if custom_data.customization.ticket_template.show_ticket_type_sequence:
            for attendee in custom_data.attendees:
                attendee['ticket_type_sequence'] = get_ticket_type_sequence(
                    attendee['barcode']
                )['ticket_type_sequence']

    if custom_data.customization.ticket_template.show_event_sequence:
        for attendee in custom_data.attendees:
            attendee['event_sequence'] = get_event_sequence(
                attendee['barcode']
            )['event_sequence']
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
    url = custom_data.template_url
    pdf = PDF(url, [data]).render().getvalue()
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
        customization = Customization.objects.get(pk=self.kwargs['pk'])
        attendees.append(dict(attendee))
        custom_data = CustomData(
            customization=customization,
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
            footer_description=[form.cleaned_data['footer_description']],
            is_test=True,
        )
        return do_send_email(custom_data)
        # Fixme: double response.
        # return HttpResponseRedirect(reverse('mails:successfully_mail'))
