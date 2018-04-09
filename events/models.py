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
    event_name = models.CharField(max_length=255)
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
