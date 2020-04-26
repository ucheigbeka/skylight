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
from threading import Thread
from kivy.core.window import Window
from sms import get_token
from sms.utils.popups import ErrorPopup


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

        # self.headers = {
        #     'Content-type': 'application/json', 'token': get_token()
        # } if not headers else headers
        self.headers = {}

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
            elif self.method == 'DELETE':
                self.resp = requests.delete(self.url, headers=self.headers)
            else:
                raise ValueError(
                    '"method" arguement must be one of "GET", "POST", "PUT" or "DELETE"')
        except requests.ConnectionError:
            msg = 'Server down'
            ErrorPopup(msg)
            # Restart server
        else:
            status_code = self.resp.status_code // 100
            if status_code in (1, 2):
                if callable(self.on_success):
                    self.on_success(self.resp)
            elif status_code in (4, 5):
                if callable(self.on_failure):
                    self.on_failure(self.resp)
                else:
                    err_resp = self.resp.json()
                    msg = r'[b]{}[/b]'.format(err_resp['title'].capitalize()
                                              ) + ' : ' + err_resp['detail']
                    ErrorPopup(msg)
        Window.set_system_cursor('arrow')
