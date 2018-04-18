# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from mock import (
    MagicMock,
    patch,
)
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from django.test import TestCase, RequestFactory
from .views import create_webhook, get_token
from django.contrib.auth.models import AnonymousUser, User


class TestCustomizations(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='edacticket',
            password='12345',
            email='edacticket@gmail.com',
            is_active=True,
        )
        self.factory = RequestFactory()
        self.auth = UserSocialAuth.objects.create(
            user=self.user, provider='eventbrite', uid="249759038146", extra_data={'access_token': 'HJDTUHYQ3ZVTVLMN52VZ'})


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
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'/webhooks/',
        )

    def test_get_token(self):
        request = self.factory.post('/customizations/create-customization/')
        request.user = self.user
        token = get_token(request)
        self.assertEquals(token, 'HJDTUHYQ3ZVTVLMN52VZ')
