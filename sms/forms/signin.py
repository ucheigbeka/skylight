import os
from base64 import b64encode
from hashlib import md5
from threading import Thread

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from packaging import version

from sms import urlTo, set_details, start_loading, stop_loading, get_username, PROJECT_ROOT, ASSETS_OUTPUT_PATH
from sms.scripts.updater import download_upgrade
from sms.setup import extract_assets, setup_poppler
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup, PopupBase, YesNoPopup, SuccessPopup

from itsdangerous import JSONWebSignatureSerializer as Serializer

SESSION_KEY = ''
SERVER_FE_VERSION = ''
CLIENT_FE_VERSION = open(os.path.join(PROJECT_ROOT, '.version')).read()

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'signin.kv')
Builder.load_file(kv_path)


def hash_key():
    session_key_sum = str(
        sum([int(x) for x in SESSION_KEY if x in "0123456789"]))
    session_bytes = bytes(session_key_sum, "utf-8")
    return b64encode(md5(session_bytes).digest()).decode("utf-8").strip("=")


def tokenize(text):
    serializer = Serializer(hash_key())
    return serializer.dumps(text).decode('utf-8')


def check_for_updates(user_initiated=False):
    server_fe = version.parse(SERVER_FE_VERSION)
    client_fe = version.parse(CLIENT_FE_VERSION)
    if server_fe > client_fe:
        YesNoPopup(f'A new version, {SERVER_FE_VERSION} exists. Current version is {CLIENT_FE_VERSION}.\n\n'
                   f'Do you want to upgrade?', on_yes=download_upgrade, title='Updater')
    elif user_initiated:
        SuccessPopup('You are on the latest version of "Student Management System"', title='Updater')
    return


class SigninWindow(FormTemplate):
    username = StringProperty()
    password = StringProperty()
    retain_session = BooleanProperty(False)
    title = 'Login'
    department = ''

    def on_enter(self, *args):
        super(SigninWindow, self).on_enter(*args)
        if not os.path.exists(ASSETS_OUTPUT_PATH):
            start_loading(text="Extracting assets...")
            extract_assets()
            stop_loading()
        setup_poppler()

    def signin(self):
        url = urlTo('login')
        token = tokenize(self.username + ':' + self.password)
        data = {'token': token}
        start_loading(text='Logging in...')
        AsyncRequest(url, on_success=self.grant_access,
                     on_failure=self.auth_error, data=data, method='POST')

    def get_session_key(self, *args):
        url = urlTo('init')
        AsyncRequest(url, on_success=self.set_token_key)

    def set_token_key(self, resp):
        init_data = resp.json()
        global SESSION_KEY, SERVER_FE_VERSION
        SESSION_KEY = init_data.get('session_key', '')
        SERVER_FE_VERSION = init_data.get('fe_version', '0.0.0')
        self.department = init_data.get('dept', '')
        self.signin()

    def grant_access(self, resp):
        data = resp.json()
        token, title = data['token'], data['title']
        set_details(self.username, token, title, self.department)
        root = App.get_running_app().root
        root.title = title

        if not self.retain_session:
            Clock.schedule_once(root.login)
        else:
            self.retain_session = False
            stop_loading()
        try:
            Thread(target=check_for_updates).start()
        except:
            pass

    def auth_error(self, resp):
        stop_loading()
        ErrorPopup('Invalid username or password')


class SigninPopupContent(BoxLayout):
    username = StringProperty()
    password = StringProperty()
    dismiss = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SigninPopupContent, self).__init__(**kwargs)
        root = App.get_running_app().root
        self.sn = root.sm.get_screen('signin')

    def signin(self):
        self.sn.username = self.username
        self.sn.password = self.password

        prev_username = get_username()
        if self.username != prev_username:
            YesNoPopup('Different user detected, incomplete works would be aborted. \n\nProceed?',
                       on_yes=self.reset, on_no=self.clear_fields)
            return
        self.sn.retain_session = True
        self.sn.get_session_key()
        self.dismiss = True

    def reset(self):
        from sms.scripts.logout import reset
        self.dismiss = True
        reset()
        self.sn.get_session_key()

    def clear_fields(self):
        self.ids.username.text = ''
        self.ids.pwd.text = ''


class SigninPopup(PopupBase):
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'Signin')
        self.content = SigninPopupContent()
        self.content.bind(dismiss=lambda ins, val: self.dismiss())
        self.size_hint = (.3, .4)
        super(SigninPopup, self).__init__(**kwargs)
