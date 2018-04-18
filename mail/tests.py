# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
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
    get_venue,
    process_data
)
from domain import CustomData


class TestMailsWithCostumization(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='edacticket',
            password='12345',
            email='edacticket@gmail.com',
            is_active=True,
        )
        self.auth = UserSocialAuth.objects.create(
            user=self.user, provider='eventbrite', uid="249759038146"
        )
        # import ipdb; ipdb.set_trace()

        self.custom_email = CustomEmail.objects.create(
            logo='27858595_2064872763530686_2522480893185786539_n.jpg',
            message='message email'

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

    @patch('mail.views.process_data')
    @patch(
        'mail.views.requests.get',
        return_value=MagicMock(
            json=MagicMock(
                return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
            )
        )
    )
    def test_get_data(self, mock_requests, mock_data):
        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            get_data(request)
        # assert eventbrite api call
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'https://www.eventbriteapi.com/v3/orders/752327237/?token=abc&expand=event,attendees',
        )

        # assert process_data
        mock_data.assert_called_once()

    @patch('mail.views.get_venue', return_value='address_1 Test')
    @patch('mail.views.do_send_email')
    def test_process_data(self, mock_do_send_mail, mock_venue):
        data = {"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392", "reserved_seating": None}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
        process_data(data)
        mock_venue.assert_called_once()
        self.assertEquals(
            mock_venue.call_args_list[0][0][0],
            u'23870984',
        )
        mock_do_send_mail.assert_called_once()

    @patch(
        'mail.views.Eventbrite.get',
        return_value=
            {
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
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            venue = get_venue('23870984')
            self.assertEquals(venue['address_1'], "address_1 Test")

            mock_requests.assert_called_once()
            self.assertEquals(
                mock_requests.call_args_list[0][0][0],
                u'/venues/23870984',
            )

    @patch(
        'mail.views.requests.get',
        return_value=MagicMock(
            json=MagicMock(
            return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
            )
        )
    )
    @patch('mail.views.get_venue', return_value='address_1 Test')
    def test_integration_data_send_mail(self, mock_venue, mock_requests):
        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            response = get_data(request)
        sended_mails = len(mail.outbox)
        self.assertEquals(sended_mails, 1)
        email = mail.outbox[0]
        from_email = email.from_email
        to_email = email.to
        self.assertEquals(from_email, 'edacticket@gmail.com')
        self.assertEquals(to_email, [u'edacticket@gmail.com'])
        self.assertEquals(response.status_code, 200)

    def test_do_send_mail(self):
        self.attendee = [{
            'attendee_first_name': 'Florencia',
            'attendee_last_name': 'Carabelli',
            'cost_gross': 0.0,
            'barcode': 16041996,
            'answers': [],
            'ticket_class': 'Ticket'
        }]
        custom_data = CustomData(
            customization_id=1,
            attendees=self.attendee,
            user_first_name='Nombre del User',
            user_last_name='Apellido del User',
            event_name_text='Nombre del evento',
            from_email='mailhostuser@gmail.com',
            event_start='2018-05-02T02:00:00Z',
            event_venue_location={'address_1': 'Lugar de evento'},
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
    @patch(
        'mail.views.requests.get',
        return_value=MagicMock(
            json=MagicMock(
                return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}}
            )
        )
    )
    @patch('mail.views.get_venue', return_value='address_1 Test')
    def test_integration_data_send_mail(self, mock_venue, mock_requests):

        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            response = get_data(request)

        sended_mails = len(mail.outbox)
        self.assertEquals(sended_mails, 0)
        self.assertEquals(response.status_code, 200)
