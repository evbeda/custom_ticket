import dropbox
import hashlib
import os.path
import time
import cStringIO
import re
import binascii

from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect

from eventbrite import Eventbrite
from PIL import Image
from urllib2 import urlopen

from customizations.models import (
    UserWebhook,
    BaseTicketTemplate,
)


def in_group(group, user):
    groups = user.groups.values()
    return group in groups.values_list('name', flat=True)


def generate_base_ticket(self):
    BaseTicketTemplate.objects.create(
        template_source='tickets/template_default.html',
        name="Default design",
        preview="../../static/images/preview_default.png",
    )
    BaseTicketTemplate.objects.create(
        template_source='tickets/hero_design.html',
        name="Hero design",
        preview="../../static/images/hero_design.png",
    )
    BaseTicketTemplate.objects.create(
        template_source='tickets/geo_design.html',
        name="Geo design",
        preview="../../static/images/geo_design.png",
    )


def get_unique_file_name(user, file_name):
    timestamp = str(int(time.time()))
    f_name = file_name.replace(' ', '-')
    h = hashlib.sha224(timestamp).hexdigest()
    name = user.first_name + '-' + \
        str(user.id) + '-' + h + '-' + f_name
    return name


def download(url, file_name):
    try:
        file_path = 'static/media/' + file_name
        r = urlopen(url)
        f = open(file_path, "wb")
        f.write(r.read())
        f.close()
        r.close()
        print "%s descargado correctamente." % file_name
        return True
    except Exception:
        print 'Unable to download file'
        return False


def valid_image_format(path):
    valid_format = ['PNG', 'JPEG']
    try:
        im = Image.open(path)
        im.close()
        return im.format in valid_format
    except IOError:
        return False


def image_exist(path):
    if valid_image_format(path):
        return os.path.exists(path)
    else:
        return False


def process_logo(logo_path, logo_url, logo_name):
    if not image_exist(logo_path):
        print 'downloading...'
        if download(logo_url, logo_name):
            print 'Downloaded. The file now exist...'
            return True
        else:
            print "Unable to download file"
            return False
    else:
        print 'file exist...'
        return True


def save_file(name, file):
    fs = FileSystemStorage()
    fs.name = fs.save(name, file)
    return fs


def upload_file(request, request_field):
    valid_type = ['image/png', 'image/jpeg']
    public_url = {}

    if request_field not in request.FILES:
        public_url['status'] = False
        public_url['dropbox'] = ''
        public_url['local'] = ''
        public_url['path'] = ''
        public_url['name'] = ''
        return public_url
    else:
        request_file = request.FILES[request_field]
        if request_file.content_type in valid_type:
            unique_name = get_unique_file_name(request.user, request_file.name)
            domain = request.build_absolute_uri('/')[:-1]
            fs = save_file(unique_name, request_file)

            public_url['name'] = unique_name
            path_file = fs.location + '/' + fs.name
            public_url['path'] = path_file

            # local
            public_url['local'] = get_file_local(domain, fs.name)

            # dropbox
            public_url['dropbox'] = upload_file_dropbox(path_file, fs.name)
            public_url['status'] = True

            return public_url
        else:
            public_url['status'] = False
            return public_url


def get_file_local(domain, file_name_saved):
    public_url = domain + settings.MEDIA_URL + file_name_saved
    return public_url


def upload_file_dropbox(path_file, file_name_saved):
    file = open(path_file, 'r')
    dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)
    res = dbx.files_upload(
        file.read(), '/' + file_name_saved,
        dropbox.files.WriteMode.add
    )
    create_shared_link = dbx.sharing_create_shared_link(res.path_display)
    link = create_shared_link.url
    url, dl = link.split('?')
    public_url = url + '?dl=1'
    return public_url


def create_webhook(token, url):
    if settings.URL_LOCAL:
        url = settings.URL_LOCAL
    data = {
        "endpoint_url": url + "/mail/mail/",
        "actions": "order.placed",
        # "event_id": "all_events",
    }
    response = Eventbrite(token).post('/webhooks/', data)
    return (response[u'id'])


def delete_webhook(token, webhook_id):
    webhook = UserWebhook.objects.get(webhook_id=webhook_id)
    webhook.delete()
    Eventbrite(token).delete('/webhooks/' + webhook_id + "/")
    return HttpResponseRedirect('/')


def get_token(user):
    token = user.social_auth.get(provider='eventbrite').access_token
    return token


def decode_image_from_base64(image_string_base64):
    try:
        image_string_base64 = re.sub(
            '^data:image/.+;base64,',
            '',
            image_string_base64,
        ).decode('base64')
        return {
            'status': True,
            'image': image_string_base64,
        }
    except binascii.Error as err:
        return {
            'status': False,
            'error': err.message,
        }


def save_image(image_string_base64):
    img_io = cStringIO.StringIO()
    image_decoded = decode_image_from_base64(image_string_base64)
    if image_decoded['status']:
        image = Image.open(cStringIO.StringIO(image_decoded['image']))
        image.save(img_io, format=image.format, quality=100)
        return img_io
    else:
        print image_decoded['error']
        return None


def get_image_and_save(image_string_base64, user):
    if bool(image_string_base64):
        image_file = save_image(image_string_base64)
        if image_file is not None:
            name_image = get_unique_file_name(user, 'imagen.jpg')
            img_content = ContentFile(
                image_file.getvalue(),
                name_image
            )
            return img_content
        else:
            return None
    else:
        return None
