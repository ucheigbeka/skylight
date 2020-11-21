import os
import requests
from kivy.lang import Builder
from kivy.core.window import Window

from sms.setup import Config
from sms.utils.popups import LoadPopup

# Backend config
# addresses: '127.0.0.1:1807', 'ucheigbeka.pythonanywhere.com:80'

# Frontend config
MODE = 'DEBUG'
kv_surfix = ''
token, title, username = '', '', ''
current_session = None
# For auto logout; time is in seconds
allowable_idle_time = 20 * 60  # 20 minutes

titles = [
    'Head of Department', 'Exam officer', '100 level course adviser',
    '200 level course adviser', '300 level course adviser',
    '400 level course adviser', '500 level course adviser',
    '500 level course adviser(2)', 'Secretary'
]
loading_popup = LoadPopup()


def start_loading(text=None):
    loading_popup.open(text=text)


def stop_loading():
    loading_popup.dismiss()


def urlTo(path):
    protocol, host, port = get_addr()
    base_url = f'{protocol}://{host}:{port}/api/'
    return base_url + path


def get_addr():
    backend_config = Config.get('backend')
    return backend_config['protocol'], backend_config['host'], backend_config['port']


def set_addr(addr):
    backend_config = dict(zip(['protocol', 'host', 'port'], addr))
    Config.put('backend', backend_config)


def get_current_session():
    global current_session
    if not current_session:
        url = urlTo('current_session')
        # AsyncRequest not used as the session is needed immediately to draw pages
        resp = requests.get(url)
        if resp.status_code == 200:
            current_session = resp.json()
    return current_session


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


def get_log(func, **kwargs):
    url = urlTo('logs')
    params = {
        'count': kwargs.pop('count', 20),
        'step': kwargs.pop('step', 0)
    }
    params.update(kwargs)
    AsyncRequest(url, params=params, on_success=func)


# Loads all the kv imports
imports_path = os.path.join(os.path.dirname(__file__),
                            'forms', 'kv_container', 'imports.kv')
Builder.load_file(imports_path)

# Sets the window's mininum size
Window.maximize()
win_size = Window.size
Window.minimum_width = win_size[0] * .7
Window.minimum_height = win_size[1] * .8

from sms.manager import Root
root = Root()
