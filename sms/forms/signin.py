import os
from base64 import b64encode
from hashlib import md5
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty

from sms import urlTo, store_token, set_title
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

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
        store_token(token)
        set_title(title)

        root = App.get_running_app().root
        root.title = title
        Clock.schedule_once(root.login)

    def auth_error(self, resp):
        ErrorPopup('Invalid username or password')

    def server_error(self, resp):
        ErrorPopup('Server down')
