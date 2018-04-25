# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-25 16:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.IntegerField(blank=True, null=True)),
                ('ticket_type_id', models.IntegerField(blank=True, null=True)),
                ('event_sequence', models.IntegerField(blank=True, null=True)),
                ('ticket_type_sequence', models.IntegerField(blank=True, null=True)),
                ('customization', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='customizations.Customization')),
            ],
        ),
    ]
