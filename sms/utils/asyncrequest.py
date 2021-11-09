"""
AsyncRequest
============

Class for making asynchronous request to the api server. The
method argument defines the type of http request to make

    method = 'GET' - for querying the database
    method = 'POST' - for adding new items to the database
    method = 'PUT' - for updating a record in the database
    method = 'DELETE' - for deleting a record from the database
"""

import requests
import json
from threading import Thread
from datetime import datetime
from kivy.core.window import Window
from sms import get_token, urlTo, ALLOWABLE_IDLE_TIME
from sms.utils.popups import ErrorPopup, YesNoPopup

last_request_timestamp = datetime.now().timestamp()
logged_in = True


class AsyncRequest(Thread):
    def __init__(self, url, on_success=None, on_failure=None, data=None,
                 params=None, headers=None, method='GET', **kwargs):
        super(AsyncRequest, self).__init__(**kwargs)

        self.url = url
        self.on_success = on_success
        self.on_failure = on_failure
        self.params = params
        self.data = data
        self.method = method
        self.resp = None

        # Reverse comment for this section during PROD
        self.headers = {
            'Content-type': 'application/json',
            'token': get_token()
        } if not headers else headers

        self.start()

    def run(self):
        Window.set_system_cursor('wait')
        # update last_request_timestamp to track activity
        session_timer(self.url, self.params)
        query_kwargs = {"url": self.url, "method": self.method,
                        "headers": self.headers}
        if self.params: query_kwargs["params"] = self.params
        if self.data: query_kwargs["json"] = self.data
        try:
            self.resp = requests.request(**query_kwargs)
            self.resp.raise_for_status()
        except requests.exceptions.ConnectionError:
            msg = 'Server down'
            ErrorPopup(msg)
            # Restart server
        except requests.exceptions.HTTPError as err:
            if self.resp.status_code == 405:
                raise ValueError('"method" argument must be one of '
                                 '"GET", "POST", "PUT" or "DELETE"')
            elif self.resp.status_code == 440:
                YesNoPopup(
                    message='Session expired, login again?',
                    on_yes=draw_sign_in_popup, title='Session Timeout'
                )
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


def session_timer(url, params):
    global last_request_timestamp, logged_in
    curr_timestamp = datetime.now().timestamp()

    if last_request_timestamp and curr_timestamp - last_request_timestamp > ALLOWABLE_IDLE_TIME:
        if url not in [urlTo('logout'), urlTo('login')] and logged_in:  # if the request is logout or login, the let it pass
            # else logout silently
            try:
                requests.post(
                    url=urlTo('logout'),
                    headers={'Content-type': 'application/json',
                             'token': get_token()},
                    json={'token': get_token()}
                )
                logged_in = False
            except requests.exceptions.ConnectionError:
                ErrorPopup('Server down')
        elif url == urlTo('login'):
            logged_in = True
    # don't update last_request_timestamp if logs is called w/o filters
    # (from main menu)
    log_filter_params = ['time', 'operation', 'reverse']
    if url != urlTo('logs') or any(map(lambda x: x in params, log_filter_params)):
        last_request_timestamp = curr_timestamp


def draw_sign_in_popup():
    from sms.forms.signin import SigninPopup
    SigninPopup()
