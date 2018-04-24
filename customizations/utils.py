import dropbox
import hashlib
import time
from urllib2 import urlopen
import os.path
from django.http import HttpResponseRedirect
from eventbrite import Eventbrite
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image


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
    request_file = request.FILES[request_field]
    public_url = {}
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

        return public_url
    else:
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


def create_webhook(token):
    data = {
        "endpoint_url": "https://custom-ticket-heroku.herokuapp.com/mail/mail/",
        "actions": "order.placed",
        # "event_id": "all_events",
    }
    response = Eventbrite(token).post('/webhooks/', data)
    return (response[u'id'])


def delete_webhook(token, webhook_id):
    Eventbrite(token).delete('/webhooks/' + webhook_id + "/")
    return HttpResponseRedirect('/')


def get_token(user):
    token = user.social_auth.get(provider='eventbrite').access_token
    return token
