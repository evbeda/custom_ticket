# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from mock import (
    MagicMock,
    patch,
)


from django.test import TestCase
from .views import create_webhook


class TestCustomizations(TestCase):
    # def test_post(self):

    @patch(
        'customizations.views.Eventbrite.post',
        return_value={
            u'user_id': u'249759038146',
            u'created': u'2018-04-13T07:19:38Z',
            u'event_id': None,
            u'resource_uri': u'https://www.eventbriteapi.com/v3/webhooks/646089/',
            u'endpoint_url': u'https://custom-ticket-heroku.herokuapp.com/mail/mail/',
            u'actions': [u'order.placed'],
            u'id': u'646089'
        }
    )
    def test_create_webhook(self, mock_requests):
        token = 'HJDTUHYQ3ZVTVLMN52VZ'
        id_webhook = create_webhook(token)

        self.assertEquals(id_webhook, '646089')

    def test_get_token(self):
        pass
