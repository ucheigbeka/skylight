import os
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from sms import urlTo, store_api_key
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'signin.kv')
Builder.load_file(kv_path)


class SigninWindow(Screen):
    form_root = form_root
    username = StringProperty()
    password = StringProperty()

    def signin(self, *args):
        url = urlTo('login')
        data = {'username': self.username, 'password': self.password}
        AsyncRequest(url, on_success=self.grant_access,
                     on_failure=self.auth_error, data=data, method='POST')

    def grant_access(self, resp):
        API_KEY = resp.json()['token']
        store_api_key(API_KEY)
        self.manager.transition.direction = 'left'
        self.manager.current = 'main_page'

    def auth_error(self, resp):
        ErrorPopup('Invalid username or password')


if __name__ == "__main__":
    from kivy.app import runTouchApp

    runTouchApp(SigninWindow())
