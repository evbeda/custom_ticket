# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class BaseTicketTemplate(TimeStampedModel):
    template_source = models.TextField()
    name = models.CharField(max_length=255)
    preview = models.CharField(max_length=255)
    content_html = models.TextField()
    aspect_ratio_logo_x = models.IntegerField(
        default=1,
        blank=False,
        null=False,
    )
    aspect_ratio_logo_y = models.IntegerField(
        default=1,
        blank=False,
        null=False,
    )
    aspect_ratio_image_x = models.IntegerField(
        default=1,
        blank=False,
        null=False,
    )
    aspect_ratio_image_y = models.IntegerField(
        default=1,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name


class TicketTemplate(TimeStampedModel):
    select_design_template = models.ForeignKey(
        BaseTicketTemplate,
        blank=True,
        null=True)
    message_ticket = models.CharField(max_length=400)
    show_event_sequence = models.BooleanField(default=False)
    show_ticket_type_sequence = models.BooleanField(default=False)
    hide_ticket_type_price = models.BooleanField(default=False)
    footer_description = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    double_ticket = models.BooleanField(default=False)


class CustomEmail(TimeStampedModel):
    message = models.TextField(max_length=800)
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
    name = models.CharField(max_length=50)
    ticket_template = models.ForeignKey(
        TicketTemplate, blank=True, null=True, on_delete=models.CASCADE
    )
    custom_email = models.ForeignKey(
        CustomEmail, blank=True, null=True, on_delete=models.CASCADE
    )
    pdf_ticket_attach = models.NullBooleanField(
        default=True, blank=True, null=True
    )


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


class DTOCustomization(object):

    def __init__(
        self,
        name,
        message,
        select_event,
        select_design_template,
        message_ticket,
        show_event_sequence,
        show_ticket_type_sequence,
        hide_ticket_type_price,
        footer_description,
        double_ticket,
        pdf_ticket_attach,
        image_partner,
        image_data,
        logo,
        customization=None,
        custom_email=None,
        ticket_template=None,
    ):
        self.select_event = select_event
        self.name_customization = name
        self.message = message
        self.select_design_template = select_design_template
        self.message_ticket = message_ticket
        self.show_event_sequence = show_event_sequence
        self.show_ticket_type_sequence = show_ticket_type_sequence
        self.hide_ticket_type_price = hide_ticket_type_price
        self.footer_description = footer_description
        self.double_ticket = double_ticket
        self.pdf_ticket_attach = pdf_ticket_attach
        self.image_partner = image_partner
        self.image_data = image_data
        self.logo = logo
        self.customization = customization
        self.custom_email = custom_email
        self.ticket_template = ticket_template
