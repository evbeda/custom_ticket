# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    '''
        An abstract base class model that provides self updating
        ``created`` and ``modified`` fields.
    '''
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class TicketTemplate(TimeStampedModel):
    select_design_template = models.CharField(max_length=255)
    message_ticket = models.CharField(max_length=255)

    @classmethod
    def data_to_dict(cls, id):
        try:
            query = CustomEmail.objects.get(pk=id)
        except Exception:
            return {}
        data = {
            'select_design_template': query.select_design_template,
            'message_ticket': query.message_ticket,
        }
        return data


class CustomEmail(TimeStampedModel):
    message = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos')

    @classmethod
    def data_to_dict(cls, id):
        try:
            query = CustomEmail.objects.get(pk=id)
        except Exception:
            return {}
        data = {
            'message': query.message,
            'logo': query.logo,
        }
        return data


class Customization(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    ticket_template = models.ForeignKey(TicketTemplate, blank=True, null=True)
    custom_email = models.ForeignKey(CustomEmail, blank=True, null=True)

    @classmethod
    def data_to_dict(cls, id):
        try:
            query = Customization.objects.get(pk=id)
        except Exception:
            return {}
        data = {
            'message': query.custom_email.message,
            'logo': query.custom_email.logo,
            'message_ticket': query.ticket_template.message_ticket,
            'select_design_template': query.ticket_template.select_design_template,
        }
        return data
