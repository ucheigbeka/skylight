'''
AsyncRequest
============

Class for making ascynchronous request to the api server. The
method arguement definies the type of http request to make

    method = 'GET' - for querying the database
    method = 'POST' - for adding new items to the database
    method = 'PUT' - for updating a record in the database
    method = 'DELETE' - for deleting a record from the database
'''

import requests
import json
from threading import Thread
from kivy.core.window import Window
from sms import get_token
from sms.utils.popups import ErrorPopup, YesNoPopup


class AsyncRequest(Thread):
    def __init__(self, url, on_success=None, on_failure=None, headers=[],
                 params=None, data=None, method='GET', **kwargs):
        super(AsyncRequest, self).__init__(**kwargs)

        self.url = url
        self.on_success = on_success
        self.on_failure = on_failure
        self.params = params
        self.data = data
        self.method = method

        # Reverse comment for this section during PROD
        self.headers = {
            'Content-type': 'application/json', 'token': get_token()
        } if not headers else headers
        # self.headers = {}

        self.start()

    def run(self):
        Window.set_system_cursor('wait')
        try:
            if self.method == 'GET':
                self.resp = requests.get(
                    self.url, headers=self.headers, params=self.params)
            elif self.method == 'POST':
                self.resp = requests.post(
                    self.url, headers=self.headers, json=self.data)
            elif self.method == 'PUT':
                self.resp = requests.put(
                    self.url, headers=self.headers, json=self.data)
            elif self.method == 'PATCH':
                self.resp = requests.patch(
                    self.url, headers=self.headers, json=self.data)
            elif self.method == 'DELETE':
                self.resp = requests.delete(
                    self.url, headers=self.headers, params=self.params)
            else:
                raise ValueError(
                    '"method" arguement must be one of "GET", "POST", "PUT" or "DELETE"')
            self.resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            msg = 'Server down'
            ErrorPopup(msg)
            # Restart server
        except requests.exceptions.HTTPError as err:
            if self.resp.status_code == 440:
                YesNoPopup(message='Session expired, login again?', on_yes=draw_sign_in_popup, title='Session Timeout')
            elif callable(self.on_failure):
                self.on_failure(self.resp)
            else:
                try:
                    err_resp = self.resp.json()
                    title = err_resp['title']
                    msg = err_resp['detail']
                except json.decoder.JSONDecodeError:
                    err = str(err)
                    title = err[:err.find(":")]
                    msg = err[err.find(":") + 1:].strip()
                except TypeError:
                    title = 'Error'
                    msg = self.resp.json()
                ErrorPopup(msg, title=title)
        else:
            if callable(self.on_success):
                self.on_success(self.resp)

        Window.set_system_cursor('arrow')


def draw_sign_in_popup():
    from kivy.app import App
    from sms.forms.signin import SigninPopup

    root = App.get_running_app().root
    signin_screen = [screen for screen in root.sm.screens if screen.name == 'signin']
    if signin_screen:
        SigninPopup(signin_screen[0])
