import os
import shutil
from io import BytesIO
from zipfile import ZipFile
from pdf2image import convert_from_bytes, convert_from_path

from sms import get_dirs
from sms.utils.preview import Preview


def generate_preview_screens(resp):
    attachment = resp.headers['Content-Disposition']
    filename = attachment[attachment.find('=') + 1:]
    io = BytesIO(resp.content)
    zf = ZipFile(io)
    filenames = sorted(zf.namelist())
    base_dir = os.path.join(get_dirs('CACHE_DIR'), os.path.splitext(filename)[0])
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
    output_dir = os.path.join(get_dirs('CACHE_DIR'), os.path.splitext(filename)[0])
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)
    paths = convert_from_bytes(pdf_content, output_folder=output_dir, fmt='jpg', thread_count=5, paths_only=True)
    filepath = os.path.join(get_dirs('CACHE_DIR'), filename)
    with open(filepath, 'wb') as fd:
        fd.write(pdf_content)

    return [Preview(name='screen {}'.format(idx), source=path, filepath=filepath) for idx, path in enumerate(paths)]
