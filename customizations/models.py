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


class BaseTicketTemplate(TimeStampedModel):
    template_source = models.TextField()
    name = models.CharField(max_length=255)
    preview = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TicketTemplate(TimeStampedModel):
    select_design_template = models.ForeignKey(
        BaseTicketTemplate,
        blank=True,
        null=True)
    message_ticket = models.CharField(max_length=255)


class CustomEmail(TimeStampedModel):
    message = models.CharField(max_length=255)
    logo = models.ImageField(max_length=255, upload_to='logos')
    logo_local = models.CharField(max_length=255)
    logo_path = models.CharField(max_length=255)
    logo_name = models.CharField(max_length=255)
    logo_url = models.CharField(max_length=255)


class Customization(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    ticket_template = models.ForeignKey(TicketTemplate, blank=True, null=True)
    custom_email = models.ForeignKey(CustomEmail, blank=True, null=True)


class UserWebhook(models.Model):
    webhook_id = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        unique=True,
    )
