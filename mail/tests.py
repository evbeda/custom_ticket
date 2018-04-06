# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mock import (
    MagicMock,
    patch,
)
from django.test import TestCase
from .views import get_data, get_venue


class TestMails(TestCase):
    @patch(
        'mail.views.Eventbrite.get',
        return_value='{'
            '"address": {'
                '"address_1": "Test",'
                '"address_2": null,'
                '"city": null,'
                '"region": null,'
                '"postal_code": null,'
                '"country": null,'
                '"latitude": "45.5121",'
                '"longitude": "-122.6771",'
                '"localized_address_display": "Test",'
                '"localized_area_display": null,'
                '"localized_multi_line_address_display": ["Test"]'
            '},'
            '"resource_uri": "https://www.eventbriteapi.com/v3/venues/23870984/",'
            '"id": "23870984",'
            '"age_restriction": null,'
            '"capacity": null,'
            '"name": null,'
            '"latitude": "45.5121",'
            '"longitude": "-122.6771"'
        '}'
    )

    @patch('mail.views.do_send_email')
    @patch('mail.views.requests.get', return_value=MagicMock(json=MagicMock(return_value={"costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/orders/752327237/", "id": "752327237", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "name": "EDAc Ticket", "first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "status": "placed", "time_remaining": None, "event_id": "44447474593", "attendees": [{"team": None, "costs": {"base_price": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "eventbrite_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "gross": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "payment_fee": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}, "tax": {"display": "$0.00", "currency": "USD", "value": 0, "major_value": "0.00"}}, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/attendees/937711035/", "id": "937711035", "changed": "2018-04-03T18:35:47Z", "created": "2018-04-03T18:35:46Z", "quantity": 1, "profile": {"first_name": "EDAc", "last_name": "Ticket", "email": "edacticket@gmail.com", "name": "EDAc Ticket", "addresses": {"home": {}, "ship": {}, "work": {}, "bill": {}}}, "barcodes": [{"status": "unused", "barcode": "752327237937711035001", "checkin_type": 0, "created": "2018-04-03T18:35:47Z", "changed": "2018-04-03T18:35:47Z"}], "answers": [], "checked_in": False, "cancelled": False, "refunded": False, "affiliate": None, "guestlist_id": None, "invited_by": None, "status": "Attending", "ticket_class_name": "FreeticketBla", "event_id": "44447474593", "order_id": "752327237", "ticket_class_id": "83644392"}], "event": {"name": {"text": "EventTest_With_FreeTicket", "html": "EventTest_With_FreeTicket"}, "description": {"text": "EVENT DESCRIPTION\u00a0\u00a0blablabla", "html": "<H3 CLASS=\"responsive-label label-primary\">EVENT DESCRIPTION\u00a0<SPAN CLASS=\"ico-info ico--small ico--color-understated js-d-tooltip text-body-small\" TITLE=\"\">\u00a0blablabla<\/SPAN><\/H3>"}, "id": "44447474593", "url": "https://www.eventbrite.com/e/eventtest-with-freeticket-tickets-44447474593", "start": {"timezone": "America/Los_Angeles", "local": "2018-05-01T19:00:00", "utc": "2018-05-02T02:00:00Z"}, "end": {"timezone": "America/Los_Angeles", "local": "2018-05-01T22:00:00", "utc": "2018-05-02T05:00:00Z"}, "organization_id": "249759038146", "created": "2018-03-22T13:44:49Z", "changed": "2018-03-22T13:45:50Z", "capacity": 100, "capacity_is_custom": False, "status": "live", "currency": "USD", "listed": True, "shareable": True, "invite_only": False, "online_event": False, "show_remaining": False, "tx_time_limit": 480, "hide_start_date": False, "hide_end_date": False, "locale": "en_US", "is_locked": False, "privacy_setting": "unlocked", "is_series": False, "is_series_parent": False, "is_reserved_seating": False, "source": "create_2.0", "is_free": True, "version": "3.0.0", "logo_id": None, "organizer_id": "17107582634", "venue_id": "23870984", "category_id": None, "subcategory_id": None, "format_id": None, "resource_uri": "https://www.eventbriteapi.com/v3/events/44447474593/"}})))
    def test_get_data(self, mock_requests, mock_do_send_email, mock_venue):
        request = MagicMock(
            body='{"config": {"action": "order.placed", "user_id": "249759038146", "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/", "webhook_id": "633079"}, "api_url": "https://www.eventbriteapi.com/v3/orders/752327237/"}'
        )
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            sent = get_data(request)

        # assert eventbrite api call
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'https://www.eventbriteapi.com/v3/orders/752327237/?token=abc&expand=event,attendee',
        )
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_venue.call_args_list[0][0][0],
            u'/venues/23870984',
        )
        # assert send email
        mock_do_send_email.assert_called_once()

    @patch(
        'mail.views.Eventbrite.get',
        return_value='{'
            '"address": {'
                '"address_1": "address_1 Test",'
                '"address_2": null,'
                '"city": null,'
                '"region": null,'
                '"postal_code": null,'
                '"country": null,'
                '"latitude": "45.5121",'
                '"longitude": "-122.6771",'
                '"localized_address_display": "Test",'
                '"localized_area_display": null,'
                '"localized_multi_line_address_display": ["Test"]'
            '},'
            '"resource_uri": "https://www.eventbriteapi.com/v3/venues/23870984/",'
            '"id": "23870984",'
            '"age_restriction": null,'
            '"capacity": null,'
            '"name": null,'
            '"latitude": "45.5121",'
            '"longitude": "-122.6771"'
        '}'
    )
    def test_get_venue(self, mock_requests):
        # request = MagicMock(
        #     body='{23870984}'
        # )
        with self.settings(SERVER_ACCESS_TOKEN='abc'):
            venue = get_venue(23870984)
            self.assertEquals(venue, "address_1 Test")

            mock_requests.assert_called_once()
            self.assertEquals(
                mock_requests.call_args_list[0][0][0],
                u'/venues/23870984',
            )
