import os
from base64 import b64encode
from hashlib import md5
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from sms import urlTo, set_details, start_loading, stop_loading, get_username
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup, PopupBase, YesNoPopup

from itsdangerous import JSONWebSignatureSerializer as Serializer

SESSION_KEY = ''

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


class SigninWindow(FormTemplate):
    username = StringProperty()
    password = StringProperty()
    title = 'Login'

    def signin(self):
        url = urlTo('login')
        token = tokenize(self.username + ':' + self.password)
        data = {'token': token}
        start_loading(text='Logging in...')
        AsyncRequest(url, on_success=self.grant_access,
                     on_failure=self.auth_error, data=data, method='POST')

    def get_session_key(self, *args):
        url = urlTo('session_key')
        AsyncRequest(url, on_success=self.set_token_key,
                     on_failure=self.server_error)

    def set_token_key(self, resp):
        global SESSION_KEY
        SESSION_KEY = resp.json()
        self.signin()

    def grant_access(self, resp):
        data = resp.json()
        token, title = data['token'], data['title']

        prev_username = get_username()
        set_details(self.username, token, title)

        kv_instance = App.get_running_app()
        root = kv_instance.root
        root.title = title

        if self.username == prev_username:
            self.dismiss()
            stop_loading()
        else:
            Clock.schedule_once(root.login)

    def auth_error(self, resp):
        stop_loading()
        ErrorPopup('Invalid username or password')

    def server_error(self, resp):
        ErrorPopup('Server down')


class SigninPopupContent(BoxLayout):
    username = StringProperty()
    password = StringProperty()
    sn = None
    dismiss = None

    def __init__(self, signin_window_object, dismiss, **kwargs):
        self.dismiss = dismiss
        self.sn = signin_window_object
        # self.ids.username.focus = True
        super().__init__(**kwargs)

    def signin(self):
        self.sn.username = self.username
        self.sn.password = self.password
        self.sn.dismiss = self.dismiss
        prev_username = get_username()
        if self.username != prev_username:
            YesNoPopup('Different user detected, incomplete works would be aborted. Proceed?',
                       on_yes=self.reset, on_no=self.clear_fields)
            return
        self.sn.get_session_key()

    def reset(self):
        from sms.scripts.logout import logout
        logout()
        self.sn.get_session_key()
        self.dismiss()

    def clear_fields(self):
        self.ids.username.text = ''
        self.ids.pwd.text = ''


class SigninPopup(PopupBase):
    def __init__(self, signin_window_object, **kwargs):
        self.title = kwargs.get('title', 'Signin')
        self.content = SigninPopupContent(signin_window_object, dismiss=self.dismiss)
        self.size_hint = (.3, .4)
        super(SigninPopup, self).__init__(**kwargs)
