# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import datetime
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


class Event(TimeStampedModel):
    # Many-to-one relationships
    # user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    eventbrite_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    date = models.DateField(default=datetime.date.today)
    location = models.CharField(max_length=255)

    def ticket_types_available(self):
        return self.ticket_types.all()


class TicketType(TimeStampedModel):
    eventbrite_id = models.CharField(max_length=255, primary_key=True)
    event = models.ForeignKey(Event, related_name='ticket_types')
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.CharField(max_length=255)

    @classmethod
    def data_to_dict(cls, id):
        try:
            query = TicketType.objects.get(pk=id)
        except Exception:
            return {}
        data = {
            'event': query.event,
            'name': query.name,
        }
        return data


class TicketTemplate(TimeStampedModel):
    name = models.CharField(max_length=255)


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
    ticket_template = models.ForeignKey(TicketTemplate)
    custom_email = models.ForeignKey(CustomEmail, blank=True, null=True)
