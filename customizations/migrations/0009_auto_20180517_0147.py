# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-17 04:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customizations', '0008_merge_20180509_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='basetickettemplate',
            name='aspect_ratio_image_x',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='basetickettemplate',
            name='aspect_ratio_image_y',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='basetickettemplate',
            name='aspect_ratio_logo_x',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='basetickettemplate',
            name='aspect_ratio_logo_y',
            field=models.IntegerField(default=1),
        ),
    ]
