import os
from kivy.lang import Builder
from kivy.core.window import Window

# Backend config
base_url = 'http://127.0.0.1:1807/api/'
# base_url = 'http://ucheigbeka.pythonanywhere.com/api/'

# Frontend config
MODE = 'DEBUG'
token, title, username = '', '', ''
kv_surfix = ''

titles = [
    'Head of Department', 'Exam officer', '100 level course adviser',
    '200 level course adviser', '300 level course adviser',
    '400 level course adviser', '500 level course adviser',
    '500 level course adviser(2)', 'Secretary'
]


def urlTo(path):
    return base_url + path


def get_current_session():
    return 2019


def get_token():
    return token


def get_username():
    return username


def set_details(_username, _token, _title):
    global username, token, title
    username = _username
    token = _token
    title = _title
    set_suffix()


def set_suffix():
    global kv_surfix
    if not title:
        kv_surfix = ''
        return
    try:
        idx = titles.index(title)
    except ValueError:
        if MODE == 'DEBUG':
            idx = 0
        else:
            raise
    idx = 2 if idx in range(2, 8) else idx
    surfixes = {
        0: '.kv',
        1: '_eo.kv',
        2: '_ca.kv',
        8: '_sec.kv'
    }
    kv_surfix = surfixes[idx]


def get_kv_path(fname):
    root = os.path.dirname(__file__)
    fpath_base = os.path.join(root, 'forms', 'kv_container')
    if kv_surfix == '.kv':
        return os.path.join(fpath_base, fname + kv_surfix)
    else:
        return os.path.join(fpath_base, 'variants', fname, fname + kv_surfix)


def get_assigned_level():
    return root.sm.assigned_level


from sms.utils.asyncrequest import AsyncRequest


def get_log(func, limit=20, offset=0):
    url = urlTo('logs')
    AsyncRequest(url, params={'limit': limit, 'offset': offset}, on_success=func)


# Loads all the kv imports
imports_path = os.path.join(os.path.dirname(
    __file__), 'forms', 'kv_container', 'imports.kv')
Builder.load_file(imports_path)

# Sets the window's mininum size
Window.maximize()
win_size = Window.size
Window.minimum_width = win_size[0] * .7
Window.minimum_height = win_size[1] * .8

from sms.manager import Root

root = Root()
