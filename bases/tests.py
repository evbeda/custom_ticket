# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from faker import Factory
from django.test import TestCase
from django.test.utils import override_settings

a = 'sdfghjkl'
SOCIAL_AUTH_EVENTBRITE_SECRET = 'Fake key'
SOCIAL_AUTH_EVENTBRITE_KEY = 'Social auth key'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'fakemail@gmail.com'
EMAIL_HOST_PASSWORD = 'fakepass'
EMAIL_USE_TLS = True
SERVER_ACCESS_TOKEN = 'server access token'
DROPBOX_ACCESS_TOKEN = 'dropbox access token'


@override_settings(
    EMAIL_HOST_USER=EMAIL_HOST_USER,
    SOCIAL_AUTH_EVENTBRITE_SECRET=SOCIAL_AUTH_EVENTBRITE_SECRET,
    SOCIAL_AUTH_EVENTBRITE_KEY=SOCIAL_AUTH_EVENTBRITE_KEY,
    EMAIL_HOST=EMAIL_HOST,
    EMAIL_PORT=EMAIL_PORT,
    EMAIL_HOST_PASSWORD=EMAIL_HOST_PASSWORD,
    EMAIL_USE_TLS=EMAIL_USE_TLS,
    SERVER_ACCESS_TOKEN=SERVER_ACCESS_TOKEN,
    DROPBOX_ACCESS_TOKEN=DROPBOX_ACCESS_TOKEN,
)
class TestBase(TestCase):
    pass
