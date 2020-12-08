import os
import sys
from glob import glob
from zipfile import ZipFile

platform = sys.platform
ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
ASSETS_OUTPUT_PATH = os.path.join(os.getcwd(), 'assets')


def extract_archived_asset(filepath):
    with ZipFile(filepath) as zf:
        zf.extractall(ASSETS_OUTPUT_PATH)


def extract_assets():
    os.mkdir(ASSETS_OUTPUT_PATH)
    assets = os.listdir(ASSETS_PATH)
    for asset in assets:
        if platform in asset:
            filepath = os.path.join(ASSETS_PATH, asset)
            fname, ext = os.path.splitext(asset)
            if ext == '.zip':
                extract_archived_asset(filepath)


def setup_poppler():
    poppler_path = glob(os.path.join(ASSETS_OUTPUT_PATH, 'poppler*'))
    if poppler_path: poppler_path = poppler_path[0]
    else: return
    environ_sep = ';' if platform == 'win32' else ':'
    os.environ['PATH'] += environ_sep + os.path.join(poppler_path, 'bin')
