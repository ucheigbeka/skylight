import os
import requests
from base64 import b64encode
from hashlib import md5
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from sms import urlTo, store_token
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

from itsdangerous import JSONWebSignatureSerializer as Serializer

SESSION_KEY = ''

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'signin.kv')
Builder.load_file(kv_path)


def set_session_key(resp):
    global SESSION_KEY
    SESSION_KEY = resp.json()


def get_session_key():
    url = urlTo('session_key')
    #AsyncRequest(url, on_success=set_session_key)
    resp = requests.get(url)
    set_session_key(resp)


def hash_key():
    session_key_sum = str(sum([int(x) for x in SESSION_KEY if x in "0123456789"]))
    session_bytes = bytes(session_key_sum, "utf-8")
    return b64encode(md5(session_bytes).digest()).decode("utf-8").strip("=")


def tokenize(text):
    serializer = Serializer(hash_key())
    return serializer.dumps(text).decode('utf-8')


class SigninWindow(Screen):
    form_root = form_root
    username = StringProperty()
    password = StringProperty()

    def signin(self, *args):
        url = urlTo('login')
        get_session_key()
        token = tokenize(self.username + ':' + self.password)
        data = {'token': token}
        AsyncRequest(url, on_success=self.grant_access,
                     on_failure=self.auth_error, data=data, method='POST')

    def grant_access(self, resp):
        token = resp.json()['token']
        store_token(token)
        self.manager.transition.direction = 'left'
        self.manager.current = 'main_page'

    def auth_error(self, resp):
        ErrorPopup('Invalid username or password')


if __name__ == "__main__":
    from kivy.app import runTouchApp

    runTouchApp(SigninWindow())
