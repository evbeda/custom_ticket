# -*- coding: utf-8 -*-

from __future__ import unicode_literals
# import requests
# import json
# from eventbrite import Eventbrite
# from django.conf import settings

from customizations.models import Customization, CustomEmail, TicketTemplate
from events.models import TicketType


def data_to_dict_customization(id):
    try:
        query = Customization.objects.get(pk=id)
    except Exception:
        return {}
    data = {
        'message': query.custom_email.message,
        'logo': query.custom_email.logo,
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
        'logo': query.logo,
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
    data = dict(
        list(data1.items()) +
        list(data2.items()) +
        list(data3.items()) +
        list(data4.items()))
    return data


# def data_model_and_api(id):
#     data1 = get_data()
#     data2 = data_to_dict_all_models(id)
#     data = dict(list(data1.items()) + list(data2.items()))
#     return data
