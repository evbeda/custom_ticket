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
    content_html = models.TextField()

    def __str__(self):
        return self.name


class TicketTemplate(TimeStampedModel):
    # select_design_template = models.CharField(max_length=255)
    select_design_template = models.ForeignKey(
        BaseTicketTemplate,
        blank=True,
        null=True)
    message_ticket = models.TextField()
    show_event_sequence = models.BooleanField(default=False)
    show_ticket_type_sequence = models.BooleanField(default=False)
    show_ticket_type_price = models.BooleanField(default=False)
    footer_description = models.TextField(blank=True, null=True)
    double_ticket = models.BooleanField(default=False)


class CustomEmail(TimeStampedModel):
    message = models.TextField()
    logo = models.ImageField(max_length=255, upload_to='logos')
    logo_local = models.CharField(max_length=255)
    logo_path = models.CharField(max_length=255)
    logo_name = models.CharField(max_length=255)
    logo_url = models.CharField(max_length=255)
    image_partner = models.ImageField(max_length=255, upload_to='partner')
    image_partner_local = models.CharField(max_length=255)
    image_partner_path = models.CharField(max_length=255)
    image_partner_name = models.CharField(max_length=255)
    image_partner_url = models.CharField(max_length=255)


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


class TicketSequence(models.Model):
    event_id = models.BigIntegerField(blank=True, null=True)
    ticket_type_id = models.BigIntegerField(blank=True, null=True)
    barcode = models.CharField(max_length=255, blank=True, null=True)
    event_sequence = models.IntegerField(blank=True, null=True)
    ticket_type_sequence = models.IntegerField(blank=True, null=True)
    customization = models.ForeignKey(Customization, blank=True)
