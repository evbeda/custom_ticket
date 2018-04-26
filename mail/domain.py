# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from customizations.models import Customization, CustomEmail, TicketTemplate
from events.models import TicketType


def data_to_dict_customization(id):
    try:
        query = Customization.objects.get(pk=id)
    except Exception:
        return {}
    data = {
        'name': query.name,
        'pdf_ticket_attach': query.pdf_ticket_attach
    }
    return data


def data_to_dict_custom_email(id):
    try:
        query = CustomEmail.objects.get(pk=id)
    except Exception:
        return {}
    data = {
        'message': query.message,
        'logo': query.logo.url,
        'logo_local': query.logo_local,
        'logo_path': query.logo_path,
        'logo_name': query.logo_name,
        'logo_url': query.logo_url,
        'image_partner': query.image_partner,
        'image_partner_local': query.image_partner_local,
        'image_partner_path': query.image_partner_path,
        'image_partner_name': query.image_partner_name,
        'image_partner_url': query.image_partner_url,
    }

    return data


def data_to_dict_ticket_template(id):
    try:
        query = TicketTemplate.objects.get(pk=id)
    except Exception:
        return {}
    data = {
        'select_design_template': query.select_design_template,
        'message_ticket': query.message_ticket,
    }
    return data


def data_to_dict_ticket_type(id):
    try:
        query = TicketType.objects.get(pk=id)
    except Exception:
        return {}
    data = {
        'event': query.event,
        'event_name': query.event.event_name,
        'date': query.event.date,
        'location': query.event.location,

        'name': query.name,
        'description': query.description,

    }
    return data


def data_to_dict_all_models(id):
    data1 = data_to_dict_ticket_type(id)
    data2 = data_to_dict_custom_email(id)
    data3 = data_to_dict_customization(id)
    data4 = data_to_dict_ticket_template(id)
    data_all_models = dict(
        list(data1.items()) +
        list(data2.items()) +
        list(data3.items()) +
        list(data4.items()))
    return data_all_models


def data_fake(id):
    data_models = data_to_dict_all_models(id)
    fake = {'attendees': [{u'answers': [],
                           u'attendee_first_name': u'James',
                           u'attendee_last_name': u'Arthur',
                           u'barcode': u'752327237937711035001',
                           u'cost_gross': 0,
                           u'ticket_class': u'Ticket Vip'}],
            # 'customization_id': 1,
            'emails': [u'testmail@mail.com'],
            'event_name_text': u'Judah & the Lion Colony House, Tall Heights',
            'event_start': u'2018-05-01T22:00:00Z',
            'event_venue_location': {u'address_1': u'815 VSt',
                                     u'address_2': u'2nd Floor',
                                     u'city': u'San Francisco',
                                     u'country': u'USA',
                                     u'latitude': u'-32.9845957',
                                     u'longitude': u'-68.78505459999997',
                                     u'postal_code': 2001,
                                     u'region': u'Bay Area'},
            'from_email': 'test@mail.com',
            'is_test': False,
            'order_created': u'2018-04-03T18:35:46Z',
            'order_id': u'752327237',
            'order_status': u'placed',
            'organizer_logo': u'',
            u'select_design_template': u'DESIGN 1',
            'ticket_class': u'',
            'user_first_name': u'Ana',
            'user_last_name': u'Campbell',
            'user_order_email': u'ana@email.com',
            'user_order_first_name': u'Ana',
            'user_order_last_name': u'Campbell',
            'footer_description': u'Tax number | Company name',
            }
    data_fake = dict(
        list(data_models.items()) +
        list(fake.items())
    )
    return data_fake


def all_data(custom_data):
    data_api = custom_data.__dict__
    data_models = data_to_dict_all_models(custom_data.customization.id)
    all_data = dict(
        list(data_api.items()) +
        list(data_models.items())
    )
    return all_data


class CustomData(object):

    def __init__(self,
                 customization=Customization(),
                 attendees=[],
                 organizer_logo='',
                 event_name_text='',
                 event_start='',
                 event_venue_location={},
                 organizer_name='',
                 organizer_email='',
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
                 barcode='',
                 user_first_name='',
                 user_last_name='',
                 venue='',
                 is_test=False,
                 footer_description='',
                 pdf_ticket_attach='',
                 ):

        self.customization = customization
        self.attendees = attendees
        self.organizer_logo = organizer_logo
        self.event_name_text = event_name_text
        self.event_start = event_start
        # self.event_end = event_end
        self.event_venue_location = event_venue_location
        self.organizer_name = organizer_name
        self.organizer_email = organizer_email
        #   reserved seating
        self.user_order_email = user_order_email
        self.order_id = order_id
        self.order_created = order_created
        self.user_order_first_name = user_order_first_name
        self.user_order_last_name = user_order_last_name
        self.user_first_name = user_first_name
        self.user_last_name = user_last_name
        self.order_status = order_status
        # payment_datetime = ''
        self.ticket_class = ticket_class
        self.from_email = from_email
        self.emails = emails
        self.is_test = is_test
        self.footer_description = footer_description
        self.pdf_ticket_attach = pdf_ticket_attach
