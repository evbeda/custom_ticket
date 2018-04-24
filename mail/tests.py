# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from unittest import skip
import json
from mock import (
    MagicMock,
    patch,
)
from social_django.models import UserSocialAuth
from django.core import mail
from django.test import TestCase, RequestFactory
from customizations.models import Customization, CustomEmail, TicketTemplate
from .views import (
    do_send_email,
    get_data,
    get_social_user,
    get_social_user_id,
    accept_webhook,
    get_venue,
    get_data,
    GetEmailTest,
    process_data,
    get_organizer,
    social_user_exists,
    webhook_available_to_process
)
from .forms import FormSendEmailPreview
from domain import CustomData


class TestBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            id=1,
            username='edacticket',
            password='12345',
            email='edacticket@gmail.com',
            is_active=True,
        )
        self.auth = UserSocialAuth.objects.create(
            user=self.user,
            provider='eventbrite',
            uid="249759038146",
            extra_data={'access_token': 'HJDTUHYQ3ZVTVLMN52VZ'}
        )
        # import ipdb; ipdb.set_trace()

        self.custom_email = CustomEmail.objects.create(
            logo='https://www.dropbox.com/s/1z832sik1oudeht/EDAc-3-40871c64b344c9650cc713492de322d5e08c896f26395a9b1e2fb16a-logo-ex-7.png?dl=1',
            message='message email',
            logo_local='http://localhost:8000/media/EDAc-3-40871c64b344c9650cc713492de322d5e08c896f26395a9b1e2fb16a-logo-ex-7.png',
            logo_name='EDAc-3-40871c64b344c9650cc713492de322d5e08c896f26395a9b1e2fb16a-logo-ex-7.png',
            logo_url='https://www.dropbox.com/s/1z832sik1oudeht/EDAc-3-40871c64b344c9650cc713492de322d5e08c896f26395a9b1e2fb16a-logo-ex-7.png?dl=1',
            logo_path='/Users/fcarabelli/eventbrite/custom_ticket/static/media/EDAc-3-40871c64b344c9650cc713492de322d5e08c896f26395a9b1e2fb16a-logo-ex-7.png',

        )
        self.ticket_template = TicketTemplate.objects.create(
            select_design_template='DESIGN 1',
            message_ticket='message'

        )
        self.customization = Customization.objects.create(
            user=self.user,
            name='Name customization',
            ticket_template=self.ticket_template,
            custom_email=self.custom_email
        )



class TestDefs(TestBase):
    def setUp(self):
        super(TestDefs, self).setUp()

    @patch('mail.views.do_send_email')
    def test_process_data(self, mock_do_send_mail):
        data = {"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392", "reserved_seating": None}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
        venue = {'address_1': 'Test'}
        organizer = 'agustin'
        user_id = 1
        process_data(data, venue, organizer, user_id)
        mock_do_send_mail.assert_called_once()

    @patch(
        'mail.views.Eventbrite.get',
        return_value={
                'address': {
                    'address_1': 'address_1 Test',
                    'address_2': 'None',
                    'city': 'None',
                    'region': 'None',
                    'postal_code': 'None',
                    'country': 'None',
                    'latitude': '5.5121',
                    'longitude': '122.6771',
                    'localized_address_display': 'est',
                    'localized_area_display': 'None',
                    'localized_multi_line_address_display': ['Test'],
                },
                'resource_uri': 'https://www.eventbriteapi.com/v3/venues/23870984/',
                'id': '3870984',
                'age_restriction': 'None',
                'capacity': 'None',
                'name': 'None',
                'latitude': '5.5121',
                'longitude': '122.6771',
        }
    )
    def test_get_venue(self, mock_requests):
        venue = get_venue('HJDTUHYQ3ZVTVLMN52VZ', '23870984')
        self.assertEquals(venue['address_1'], "address_1 Test")

        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'/venues/23870984',
        )

    def test_webhook_available_to_process(self):
        user_id = '249759038146'
        self.assertTrue(webhook_available_to_process(user_id))

    def test_webhook_not_available_to_process(self):
        user_id = '24975909876543'
        self.assertFalse(webhook_available_to_process(user_id))

    def test_social_user_exists(self):
        user_id = '249759038146'
        self.assertTrue(social_user_exists(user_id))

    def test_social_user_not_exists(self):
        user_id = '24975909876543'
        self.assertFalse(social_user_exists(user_id))

    def test_get_social_user_id(self):
        social_user_id=get_social_user_id('249759038146')
        self.assertEquals(social_user_id, 1)

    @patch(
        'mail.views.Eventbrite.get',
        return_value={
            "description": {
                "text": None,
                "html": None
            },
            "long_description": {
                "text": None,
                "html": "<P>"
            },
            "logo": {
                "crop_mask": None,
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F42050011%2F203801646664%2F2%2Foriginal.jpg?auto=compress&s=de1a37d8677ceed6c7935e1e7b28b513",
                    "width": 1080,
                    "height": 1080
                },
                "id": "42050011",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F42050011%2F203801646664%2F2%2Foriginal.jpg?h=200&w=200&auto=compress&s=3a090299cc49a55ce6d6ba597a719733",
                "aspect_ratio": "1",
                "edge_color": "#1a1a1a",
                "edge_color_set": True
            },
            "resource_uri": "https://www.eventbriteapi.com/v3/organizers/13035972485/",
            "id": "13035972485",
            "name": "Harlem Producciones",
            "url": "https://www.eventbrite.com.ar/o/harlem-producciones-13035972485",
            "vanity_url": "http://harlemproduce.eventbrite.com",
            "num_past_events": 0,
            "num_future_events": 0,
            "twitter": "@harlemproduce",
            "facebook": "harlemproduce",
            "instagram": "2053900849",
            "logo_id": "42050011",
        }
    )
    def test_get_organizer(self, mock_organizer):
        organizer = get_organizer('HJDTUHYQ3ZVTVLMN52VZ', '13035972485')
        self.assertEquals(organizer, 'Harlem Producciones')
        mock_organizer.assert_called_once()
        self.assertEquals(
            mock_organizer.call_args_list[0][0][0],
            u'/organizers/13035972485',
        )

    @patch('mail.views.get_organizer', return_value='agustin')
    @patch('mail.views.get_venue', return_value={'address_1 Test'})
    @patch('mail.views.process_data')
    @patch(
        'mail.views.requests.get',
        return_value=MagicMock(
            json=MagicMock(
                return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
            )
        )
    )
    def test_get_data(self, mock_requests, mock_data, mock_venue, mock_organizer):
        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='HJDTUHYQ3ZVTVLMN52VZ'):
            get_data(request.body)
        # assert eventbrite api call
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'https://www.eventbriteapi.com/v3/orders/752327237/?token=HJDTUHYQ3ZVTVLMN52VZ&expand=event,attendees',
        )


class TestMailsWithCostumization(TestBase):
    def setUp(self):
        super(TestMailsWithCostumization, self).setUp()

    @patch('mail.views.get_organizer', return_value='agustin')
    @patch('mail.views.get_venue', return_value={'address_1 Test'})
    @patch('mail.views.process_data')
    @patch(
        'mail.views.requests.get',
        return_value=MagicMock(
            json=MagicMock(
                return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
            )
        )
    )
    def test_get_data(self, mock_requests, mock_data, mock_venue, mock_organizer):
        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='HJDTUHYQ3ZVTVLMN52VZ'):
            get_data(request.body)
        # assert eventbrite api call
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'https://www.eventbriteapi.com/v3/orders/752327237/?token=HJDTUHYQ3ZVTVLMN52VZ&expand=event,attendees',
        )

        # assert process_data
        mock_data.assert_called_once()
        mock_venue.assert_called_once()

    @patch('customizations.utils.download', return_value=True)
    @patch(
        'mail.views.requests.get',
        return_value=MagicMock(
            json=MagicMock(
            return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
            )
        )
    )
    @patch('mail.views.get_venue', return_value='address_1 Test')
    @patch('mail.views.get_organizer', return_value='agustin')
    def test_integration_data_send_mail(self, mock_organizer, mock_venue, mock_requests, mock_download):
        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        response = get_data(request.body)
        sended_mails = len(mail.outbox)
        self.assertEquals(sended_mails, 1)
        email = mail.outbox[0]
        from_email = email.from_email
        to_email = email.to
        self.assertEquals(from_email, 'edacticket@gmail.com')
        self.assertEquals(to_email, [u'edacticket@gmail.com'])
        self.assertEquals(response.status_code, 200)

    @patch('customizations.utils.download', return_value=True)
    def test_do_send_mail(self, mock_download):
        self.attendee = [{
            'attendee_first_name': 'Florencia',
            'attendee_last_name': 'Carabelli',
            'cost_gross': 0.0,
            'barcode': 16041996,
            'answers': [],
            'ticket_class': 'Ticket'
        }]
        customization = Customization.objects.filter(user_id=self.user.id)
        custom_data = CustomData(
            customization_id=customization[0].id,
            attendees=self.attendee,
            user_first_name='Nombre del User',
            user_last_name='Apellido del User',
            event_name_text='Nombre del evento',
            from_email='mailhostuser@gmail.com',
            event_start='2018-05-02T02:00:00Z',
            event_venue_location={'address_1': 'Lugar de evento'},
            organizer_name='Organizer',
            organizer_email='Organizer@gmail.com',
            emails=['unmail@gmail.com'],
            order_id='1234567890',
            order_created='2018-04-02T02:00:00Z',
            order_status='placed',
            is_test=False,
        )
        response = do_send_email(custom_data)
        self.assertEquals(response.status_code, 200)
        email = mail.outbox[0]
        from_email = email.from_email
        to_email = email.to
        self.assertEquals(from_email, 'mailhostuser@gmail.com')
        self.assertEquals(to_email, ['unmail@gmail.com'])


class TestMailWithoutCustomization(TestCase):

    @patch('customizations.utils.download', return_value=True)
    def test_integration_data_send_mail(self, mock_download):

        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            response = accept_webhook(request)
        self.assertEquals(response.status_code, 200)
