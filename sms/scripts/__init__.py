import os
from io import BytesIO
from zipfile import ZipFile

from sms.utils.preview import Preview

cache_dir = os.path.join(os.path.expanduser('~'), 'sms')


def generate_preview_screens(resp):
    io = BytesIO(resp.content)
    zf = ZipFile(io)
    filenames = sorted(zf.namelist())
    zf.extractall(cache_dir)

    screens = []
    for idx, filename in enumerate(filenames):
        filepath = os.path.join(cache_dir, filename)
        screens.append(Preview(name='screen {}'.format(idx), source=filepath))

    return screens


def generate_preview(resp):
    attachment = resp.headers['Content-Disposition']
    filename = attachment[attachment.find('=') + 1:]
    img = resp.content
    filepath = os.path.join(cache_dir, filename)
    with open(filepath, 'wb') as fd:
        fd.write(img)

    return [Preview(name='screen {}'.format(1), source=filepath)]
