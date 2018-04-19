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
        'message_ticket': query.ticket_template.message_ticket,
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


def all_data(custom_data):
    data_api = custom_data.__dict__
    data_models = data_to_dict_all_models(custom_data.customization_id)
    all_data = dict(
        list(data_api.items()) +
        list(data_models.items())
    )
    return all_data


class CustomData(object):

    def __init__(self,
                 customization_id=0,
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
                 barcode='',
                 user_first_name='',
                 user_last_name='',
                 venue='',
                 is_test=False
                 ):

        self.customization_id = customization_id
        self.attendees = attendees
        self.organizer_logo = organizer_logo
        self.event_name_text = event_name_text
        self.event_start = event_start
        # self.event_end = event_end
        self.event_venue_location = event_venue_location
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
        self.venue = venue
        self.is_test = is_test
