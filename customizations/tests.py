# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import BytesIO
import shutil
import tempfile
import base64
import cStringIO
from unittest import skipIf
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test.utils import override_settings
from faker import Factory
from freezegun import freeze_time
from mock import (
    patch,
    Mock,
)
from os import path
from PIL import Image
from social_django.models import UserSocialAuth
from django.test import TestCase, RequestFactory

from customizations.forms import FormCustomization
from customizations.models import UserWebhook, BaseTicketTemplate
from customizations.utils import (
    create_webhook,
    delete_webhook,
    download,
    get_token,
    get_unique_file_name,
    image_exist,
    valid_image_format,
    decode_image_from_base64,
    save_image,
    get_image_and_save,
)
import os


class TestBase(TestCase):
    def setUp(self):
        fake = Factory.create()
        self.user = get_user_model().objects.create_user(
            username=fake.name(),
            password='12345',
            email=fake.email(),
            first_name='test_user',
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        group_name = "admins"
        self.group = Group(name=group_name)
        self.group.save()
        self.user.groups.add(self.group)
        self.group.user_set.add(self.user)
        self.user.set_password('hello')
        self.user.save()
        self.user_access_token = 'HJDTUHYQ3ZVTVLMN52VZ'
        self.factory = RequestFactory()
        self.auth = UserSocialAuth.objects.create(
            user=self.user,
            provider='eventbrite',
            uid="249759038146",
            extra_data={
                'access_token': 'HJDTUHYQ3ZVTVLMN52VZ',
            },
        )
        login = self.client.login(
            username=self.user.username,
            password='hello',
        )
        return login


@override_settings(STATICFILES_STORAGE=None)
class IndexViewTest(TestBase):

    def setUp(self):
        super(IndexViewTest, self).setUp()
        BaseTicketTemplate.objects.create(
            template_source="Test",
            name="Test",
            preview="Test",
            content_html="Test",
        )
        self.file = cStringIO.StringIO()
        size = (200, 200)
        color = (255, 0, 0, 0)
        self.image = Image.new("RGBA", size, color)
        self.image.save(self.file, format='PNG')
        self.temp_image = self.file
        prefix = 'data:image/png;base64,'
        self.base64_string = base64.b64encode(self.file.getvalue())
        self.image_base64_string = prefix + self.base64_string
        self.image_content = get_image_and_save(
            self.image_base64_string, self.user
        )

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_no_customizations(self):
        response = self.client.get('/')
        self.assertContains(
            response,
            "You don't have any customization created yet"
        )

    @patch(
        'customizations.views.upload_file',
        return_value={
            'path': u'/path/image/image.png',
            'local': u'http://localhost:8000/image.png',
            'name': u'image.png',
            'dropbox': u'https://www.dropbox.com/s/image.png?dl=1',
            'status': True,
        }
    )
    @skipIf(True, "I don't want to run this test yet")
    @patch(
        'customizations.services.upload_file_dropbox',
        return_value='www.image.com',
    )
    @patch(
        'customizations.services.get_token',
        return_value='HJDTUHYQ3ZVTVLMN52VZ',
    )
    @patch(
        'customizations.services.create_webhook',
        return_value='646089',
    )
    @patch(
        'customizations.views.upload_file',
        return_value={
            'path': u'/path/image/image.png',
            'local': u'http://localhost:8000/image.png',
            'name': u'image.png',
            'dropbox': u'https://www.dropbox.com/s/image.png?dl=1',
            'status': True,
        }
    )
    def test_post(
            self,
            mock_upload_file_services,
            mock_webhook,
            mock_token,
            mock_upload_drop,
            mock_upload_file_views,
    ):
        with patch(
                'customizations.services.get_image_and_save',
                return_value=self.image_content,
        ) as mock_image_save:

            img = BytesIO(b'mybinarydata')
            img.name = 'logo.jpg'
            file = cStringIO.StringIO()
            size = (200, 200)
            color = (255, 0, 0, 0)
            image = Image.new("RGBA", size, color)
            image.save(file, format='PNG')
            prefix = 'data:image/png;base64,'
            base64_string = base64.b64encode(file.getvalue())
            image_base64_string = prefix + base64_string
            response = self.client.post(
                '/customizations/create-customization/',
                data={
                    u'name': [u'prueba'],
                    u'show_ticket_type_sequence': [u'on'],
                    u'hide_ticket_type_price': [u'on'],
                    u'select_event': [u'Apply All Events'],
                    u'message_ticket': [u'prueba ticket'],
                    u'image_data': image_base64_string,
                    u'footer_description': [u'asdasd'],
                    u'show_event_sequence': [u'on'],
                    u'create_customization': [u'Create'],
                    u'select_design_template': [u'1'],
                    u'csrfmiddlewaretoken': [u'b7wtBfWYFKjKBruuaS3JMOi1'],
                    u'message': [u'prueba mensaje'],
                    'logo': img,
                    'image_partner': img,
                    'pdf_ticket_attach': True,
                },
                follow=True,
            )
            os.remove(
                'static/media/partner/' +
                mock_image_save.return_value.name
            )

            mock_webhook.assert_called_once()
            self.assertEquals(200, response.status_code)

    @patch(
        'customizations.utils.Eventbrite.post',
        return_value={
            u'user_id': u'249759038146',
            u'created': u'2018-04-13T07:19:38Z',
            u'event_id': None,
            u'resource_uri': u'https://www.eventbriteapi.com/v3/',
            u'endpoint_url': u'https://app/endpint',
            u'actions': [u'order.placed'],
            u'id': u'646089'
        }
    )
    def test_create_webhook(self, mock_requests):
        token = 'HJDTUHYQ3ZVTVLMN52VZ'
        id_webhook = create_webhook(token, 'http://localhost:8000')
        self.assertEquals(id_webhook, '646089')
        mock_requests.assert_called_once()
        self.assertEquals(
            mock_requests.call_args_list[0][0][0],
            u'/webhooks/',
        )

    def test_get_token(self):
        request = self.factory.post('/customizations/create-customization/')
        request.user = self.user
        token = get_token(request.user)
        self.assertEquals(token, self.user_access_token)

    @freeze_time("2012-01-14 03:21:34")
    def test_get_unique_file_name(self):
        request = self.factory.post('/customizations/create-customization/')
        self.user.id = 4
        request.user = self.user
        unique_name = get_unique_file_name(
            request.user, 'nombre del archivo.png')
        self.assertEquals(
            unique_name,
            'test_user-4-e4122a5c7387fc823e534bdfa600f1' +
            '76cef7cb27732f90323cba4b29-nombre-del-archivo.png'
        )


class TestFormCustomization(TestCase):
    def test_form(self):
        form_data = {
            'name': 'testform',
            'select_event': 'Apply to All',
            'logo': None,
            'message': 'Test',
            'select_design_template': 'Default Design',
            'message_ticket': 'Test',
            'image_partner': None,
            'pdf_ticket_attach': True,
        }
        form = FormCustomization(form_data)
        self.assertTrue(form.is_valid)

    def test_form_false(self):
        form_data = {}
        form = FormCustomization(form_data)
        self.assertTrue(form.is_valid)


class TestCustomizationsWithWebhook(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='edacticket',
            password='12345',
            email='edacticket@gmail.com',
            first_name='edacticket',
            is_active=True,
        )
        self.user_access_token = 'HJDTUHYQ3ZVTVLMN52VZ'
        self.factory = RequestFactory()
        self.auth = UserSocialAuth.objects.create(

            user=self.user,
            provider='eventbrite',
            uid="249759038146",
            extra_data={'access_token': 'HJDTUHYQ3ZVTVLMN52VZ'}
        )
        self.webhook = UserWebhook.objects.create(
            user=self.user,
            webhook_id='646089',
        )

    @patch(
        'customizations.utils.get_token',
        return_value='HJDTUHYQ3ZVTVLMN52VZ',
    )
    @patch('customizations.utils.create_webhook', return_value='646089')
    def test_post(self, mock_webhook, mock_token):
        request = self.factory.post('/customizations/create-customization/')
        request.user = self.user
        mock_token.assert_not_called()
        mock_webhook.assert_not_called()

    def test_delete_webhook(self):
        token = 'HJDTUHYQ3ZVTVLMN52VZ'
        webhook_id = '646089'
        response = delete_webhook(token, webhook_id)
        self.assertEquals(response.status_code, 302)


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


class TestUtils(TestCase):
    def setUp(self):
        fake = Factory.create()
        self.user = get_user_model().objects.create_user(
            username=fake.name(),
            password='12345',
            email=fake.email(),
            first_name='test_user',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.file = cStringIO.StringIO()
        size = (200, 200)
        color = (255, 0, 0, 0)
        self.image = Image.new("RGBA", size, color)
        self.image.save(self.file, format='PNG')
        self.temp_image = self.file
        prefix = 'data:image/png;base64,'
        self.base64_string = base64.b64encode(self.file.getvalue())
        self.image_base64_string = prefix + self.base64_string

    def tearDown(self):
        self.file.close()

    def test_success_decode_image_from_base64(self):
        image_decoded = decode_image_from_base64(self.image_base64_string)
        self.assertEquals(image_decoded['status'], True)

    def test_error_decode_image_from_base64(self):
        image_decoded = decode_image_from_base64('test string')
        self.assertEquals(image_decoded['status'], False)

    def test_save_image_from_base64(self):
        image_file = save_image(self.image_base64_string)
        self.assertEquals(image_file is None, False)

    def test_get_image_and_save_from_base64(self):
        image_content = get_image_and_save(self.image_base64_string, self.user)
        self.assertEquals(image_content is None, False)

    def test_get_image_and_save_from_empty_string(self):
        image_content = get_image_and_save('', self.user)
        self.assertEquals(image_content is None, True)

    def test_get_image_and_save_from_false_string(self):
        image_content = get_image_and_save('test_string_no_base_64', self.user)
        self.assertEquals(image_content is None, True)
