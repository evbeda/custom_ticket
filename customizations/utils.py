import dropbox
import hashlib
import time
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def get_unique_file_name(user, file_name):
    timestamp = str(int(time.time()))
    f_name = file_name.replace(' ', '-')
    h = hashlib.sha224(timestamp).hexdigest()
    name = user.first_name + '-' + \
        str(user.id) + '-' + h + '-' + f_name
    return name


def upload_file(request, request_field):

    public_url = ''
    fs = FileSystemStorage()
    request_file = request.FILES[request_field]
    unique_name = get_unique_file_name(request.user, request_file.name)
    file_name_saved = fs.save(unique_name, request_file)
    domain = request.build_absolute_uri('/')[:-1]

    if settings.LOCAL_STORAGE_ENABLE:
        public_url = domain + settings.MEDIA_URL + file_name_saved

    else:
        path_file = fs.location + '/' + file_name_saved
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
