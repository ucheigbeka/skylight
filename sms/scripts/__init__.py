import os
import shutil
from io import BytesIO
from zipfile import ZipFile
from pdf2image import convert_from_bytes, convert_from_path

from sms.utils.preview import Preview

cache_dir = os.path.join(os.path.expanduser('~'), 'sms', 'cache')
BACKUP_DIR = os.path.join(os.path.expanduser('~'), 'sms', 'backups')
for _dir in cache_dir, BACKUP_DIR:
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    elif _dir != BACKUP_DIR:
        shutil.rmtree(_dir, ignore_errors=True)
        os.makedirs(_dir, exist_ok=True)


def generate_preview_screens(resp):
    attachment = resp.headers['Content-Disposition']
    filename = attachment[attachment.find('=') + 1:]
    io = BytesIO(resp.content)
    zf = ZipFile(io)
    filenames = sorted(zf.namelist())
    base_dir = os.path.join(cache_dir, os.path.splitext(filename)[0])
    os.makedirs(base_dir)
    zf.extractall(base_dir)

    screens = []
    for idx, filename in enumerate(filenames):
        filepath = os.path.join(base_dir, filename)
        img_path_list = convert_from_path(filepath, output_folder=base_dir, fmt='png', thread_count=5, paths_only=True)
        screens.append(Preview(name='screen {}'.format(idx), source=img_path_list[0]))

    return screens


def generate_preview(resp):
    attachment = resp.headers['Content-Disposition']
    filename = attachment[attachment.find('=') + 1:]
    pdf_content = resp.content
    output_dir = os.path.join(cache_dir, os.path.splitext(filename)[0])
    os.makedirs(output_dir)
    paths = convert_from_bytes(pdf_content, output_folder=output_dir, fmt='jpg', thread_count=5, paths_only=True)
    filepath = os.path.join(cache_dir, filename)
    with open(filepath, 'wb') as fd:
        fd.write(pdf_content)

    return [Preview(name='screen {}'.format(idx), source=path, filepath=filepath) for idx, path in enumerate(paths)]
