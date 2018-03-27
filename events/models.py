# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth import get_user_model
import datetime
from django.conf import settings

# docs model django 1.11
# https://docs.djangoproject.com/en/1.11/topics/db/models/


class Event(models.Model):
    # Many-to-one relationships
    # user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    eventbrite_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    date = models.DateField(default=datetime.date.today)
    location = models.CharField(max_length=255)


class TicketType(models.Model):
    eventbrite_id = models.CharField(max_length=255, primary_key=True)
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.CharField(max_length=255)


class TicketTemplate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)


class EmailConfirmation(models.Model):
    message = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)


class Customization(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    ticket_template = models.ForeignKey(TicketTemplate)
    email_confirmation = models.ForeignKey(EmailConfirmation)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)