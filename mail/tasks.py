import datetime
import json
import requests
import time
from customizations.models import (
    Customization,
    TicketSequence,
)
from customizations.utils import process_logo
from custom_ticket.celery import app
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import (
    BadHeaderError,
    EmailMessage,
)
from django.core.urlresolvers import reverse as r
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.template.loader import render_to_string
from social_django.models import UserSocialAuth
from eventbrite import Eventbrite
from mail.domain import (
    all_data,
    CustomData,
)
from mail.utils import PDF


@app.task(ignore_result=True)
def get_data(body, domain):
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
            domain=domain,
            order=data.json(),
            venue=venue,
            organizer=organizer,
            user_id=get_social_user_id(user_id)
        )


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


def process_data(domain, order, venue, organizer, user_id):
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
        domain=domain,
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


def do_send_email(custom_data):
    data = all_data(custom_data)
    if not data['logo_path'] is u'':
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

    if data['pdf_ticket_attach'] is True:
        pdf = PDF(url, [data]).render().getvalue()
        email.attach('ticket', pdf, 'application/pdf')
    else:
        pass
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
