import os
import sys
from glob import glob
from zipfile import ZipFile

platform = sys.platform
assets_path = os.path.join(os.path.dirname(__file__), 'assets')
output_path = os.path.join(os.getcwd(), 'assets')


def extract_archived_asset(filepath):
    with ZipFile(filepath) as zf:
        zf.extractall(output_path)


def extract_assets():
    os.mkdir(output_path)
    assets = os.listdir(assets_path)
    for asset in assets:
        if platform in asset:
            filepath = os.path.join(assets_path, asset)
            fname, ext = os.path.splitext(asset)
            if ext == '.zip':
                extract_archived_asset(filepath)


def setup_poppler():
    poppler_path = glob(os.path.join(output_path, 'poppler*'))[0]
    environ_sep = ';' if platform == 'win32' else ':'
    os.environ['PATH'] += environ_sep + os.path.join(poppler_path, 'bin')
