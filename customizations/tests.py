# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import BytesIO
import json
import shutil
import tempfile
from mock import (
    MagicMock,
    patch,
    Mock,
    mock_open,
)
from .utils import create_webhook, get_token, delete_webhook
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from social_django.models import UserSocialAuth
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from .forms import FormCustomization
from .utils import (
    get_unique_file_name,
    upload_file,
    image_exist,
    valid_image_format,
    download,
)
from freezegun import freeze_time
from .models import UserWebhook
from .views import ViewCreateCustomization
from PIL import Image
from os import path


# class TestBase(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             username='edacticket',
#             password='12345',
#             email='edacticket@gmail.com',
#             first_name='edacticket',
#             is_active=True,
#             is_staff=True,
#             is_superuser=True
#         )
#         self.user.set_password('hello')
#         self.user.save()
#         self.user_access_token = 'HJDTUHYQ3ZVTVLMN52VZ'
#         self.factory = RequestFactory()
#         self.auth = UserSocialAuth.objects.create(
#             user=self.user,
#             provider='eventbrite',
#             uid="249759038146",
#             extra_data={'access_token': 'HJDTUHYQ3ZVTVLMN52VZ'}
#         )
#         login = self.client.login(username='edacticket', password='hello')
#         return login


# @override_settings(STATICFILES_STORAGE=None)
# class IndexViewTest(TestBase):

#     def setUp(self):
#         super(IndexViewTest, self).setUp()

#     def test_homepage(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)

#     def test_no_customizations(self):
#         response = self.client.get('/')
#         self.assertContains(response, "You don't have any customization created yet")

#     @patch('customizations.views.get_token', return_value='HJDTUHYQ3ZVTVLMN52VZ')
#     @patch('customizations.views.create_webhook', return_value='646089')
#     @patch('customizations.views.upload_file', return_value={'path': u'/Users/asaiz/eventbrite/custom_ticket/static/media/EDAc-1-631b830c043352f057c4da164cf20b3227a88870603bbd3edb1d94bc-Foto-1.png', 'local': u'http://localhost:8000/media/EDAc-1-631b830c043352f057c4da164cf20b3227a88870603bbd3edb1d94bc-Foto-1.png', 'name': u'EDAc-1-631b830c043352f057c4da164cf20b3227a88870603bbd3edb1d94bc-Foto-1.png', 'dropbox': u'https://www.dropbox.com/s/2h44xdq9x6466ip/EDAc-1-631b830c043352f057c4da164cf20b3227a88870603bbd3edb1d94bc-Foto-1.png?dl=1'})
#     def test_post(self, mock_upload_file, mock_webhook, mock_token):
#         img = BytesIO(b'mybinarydata')
#         img.name = 'myimage.jpg'
#         response = self.client.post(
#             '/customizations/create-customization/',
#             data={
#                 u'name': [u'prueba'],
#                 u'select_event': [u'Apply All Events'],
#                 u'message_ticket': [u'prueba ticket'],
#                 u'create_customization': [u'Create'],
#                 u'select_design_template': [u'DESIGN 1'],
#                 u'csrfmiddlewaretoken': [u'b7wtBfWYFKGkxNxDPrwS8WLZxv001isUjKBrCvrjg9ZibLSKaru2ozuuaS3JMOi1'],
#                 u'message': [u'prueba mensaje'],
#                 'logo': img,
#             },
#             follow=True,
#         )

#         mock_token.assert_called_once()
#         mock_webhook.assert_called_once()
#         mock_upload_file.assert_called_once()
#         self.assertEquals(200, response.status_code)

#     @patch(
#         'customizations.utils.Eventbrite.post',
#         return_value={
#             u'user_id': u'249759038146',
#             u'created': u'2018-04-13T07:19:38Z',
#             u'event_id': None,
#             u'resource_uri': u'https://www.eventbriteapi.com/v3/webhooks/646089/',
#             u'endpoint_url': u'https://custom-ticket-heroku.herokuapp.com/mail/mail/',
#             u'actions': [u'order.placed'],
#             u'id': u'646089'
#         }
#     )
#     def test_create_webhook(self, mock_requests):
#         token = 'HJDTUHYQ3ZVTVLMN52VZ'
#         id_webhook = create_webhook(token)
#         self.assertEquals(id_webhook, '646089')
#         mock_requests.assert_called_once()
#         self.assertEquals(
#             mock_requests.call_args_list[0][0][0],
#             u'/webhooks/',
#         )

#     def test_get_token(self):
#         request = self.factory.post('/customizations/create-customization/')
#         request.user = self.user
#         token = get_token(request.user)
#         self.assertEquals(token, self.user_access_token)

#     @freeze_time("2012-01-14 03:21:34")
#     def test_get_unique_file_name(self):
#         request = self.factory.post('/customizations/create-customization/')
#         request.user = self.user
#         unique_name = get_unique_file_name(request.user, 'nombre del archivo.png')
#         self.assertEquals(
#             unique_name,
#             'edacticket-3-e4122a5c7387fc823e534bdfa600f176cef7cb27732f90323cba4b29-nombre-del-archivo.png'
#         )


# class TestFormCustomization(TestCase):
#     def test_form(self):
#         form_data = {'name': 'testform', 'select_event': 'Apply to All', 'logo': None, 'message': 'Test', 'select_design_template': 'Default Design', 'message_ticket': 'Test'}
#         form = FormCustomization(form_data)
#         self.assertTrue(form.is_valid)

#     def test_form_false(self):
#         form_data = {}
#         form = FormCustomization(form_data)
#         self.assertTrue(form.is_valid)


# class TestCustomizationsWithWebhook(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             username='edacticket',
#             password='12345',
#             email='edacticket@gmail.com',
#             first_name='edacticket',
#             is_active=True,
#         )
#         self.user_access_token = 'HJDTUHYQ3ZVTVLMN52VZ'
#         self.factory = RequestFactory()
#         self.auth = UserSocialAuth.objects.create(

#             user=self.user,
#             provider='eventbrite',
#             uid="249759038146",
#             extra_data={'access_token': 'HJDTUHYQ3ZVTVLMN52VZ'}
#         )
#         self.webhook = UserWebhook.objects.create(
#             user=self.user,
#             webhook_id='646089'
#         )

#     @patch('customizations.utils.get_token', return_value='HJDTUHYQ3ZVTVLMN52VZ')
#     @patch('customizations.utils.create_webhook', return_value='646089')
#     def test_post(self, mock_webhook, mock_token):
#         request = self.factory.post('/customizations/create-customization/')
#         request.user = self.user
#         mock_token.assert_not_called()
#         mock_webhook.assert_not_called()

#     def test_delete_webhook(self):
#         token = 'HJDTUHYQ3ZVTVLMN52VZ'
#         webhook_id = '646089'
#         response = delete_webhook(token, webhook_id)
#         self.assertEquals(response.status_code, 302)


class TestDropboxHandler(TestCase):
    def setUp(self):
        self.files = [Mock(filename='image.png')]
        self.rq = RequestFactory()
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        temp_file = tempfile.NamedTemporaryFile()
        size = (200, 200)
        color = (255, 0, 0, 0)
        image = Image.new("RGBA", size, color)
        image.save(temp_file, 'png')
        self.temp_image = temp_file

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_image_exist(self):
        self.assertEquals(image_exist(self.temp_image.name), True)

    def test_image_no_exist(self):
        path = "error.png"
        self.assertEquals(image_exist(path), False)

    def test_image_exist_wrong_format(self):
        # Create a file in the temporary directory
        f = open(path.join(self.test_dir, 'test.txt'), 'w')
        self.assertEquals(image_exist(f.name), False)

    def test_image_format(self):
        # Create a file in the temporary directory
        self.assertEquals(valid_image_format(self.temp_image.name), True)

    def test_image_wrong_format(self):
        # Create a file in the temporary directory
        f = open(path.join(self.test_dir, 'test.txt'), 'w')
        self.assertEquals(valid_image_format(f.name), False)

    @patch('customizations.utils.open')
    @patch('customizations.utils.urlopen')
    def test_download_image_from_url(self, mock_urlopen, mock_openfile):
        res = download('www.url.com', 'image_name.png')
        self.assertEquals(res, True)
