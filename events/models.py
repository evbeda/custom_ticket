# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# docs model django 1.11
# https://docs.djangoproject.com/en/1.11/topics/db/models/


class UserModel(models.Model):
    # By default, Django gives each model the following field:
    # auto-incrementing primary key.
    # id = models.AutoField(primary_key=True)
    field_name = models.CharField(max_length=30)


class EventModel(models.Model):
    # Many-to-one relationships
    # user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    pass


class TicketTypeModel(models.Model):
    pass


class CustomizationModel(models.Model):
    pass


class TicketTemplateModel(models.Model):
    pass


class EmailConfirmationModel(models.Model):
    pass
