import os
from kivy.lang import Builder

from sms import urlTo, get_username
from sms.forms.signin import tokenize
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup, SuccessPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'profile.kv')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class Profile(FormTemplate):
    title = 'Profile'

    def __init__(self, **kwargs):
        super(Profile, self).__init__(**kwargs)
        self.username = get_username()
        self.data = {}

    def on_enter(self):
        self.query_profile()

    def query_profile(self, *args):
        url = urlTo('accounts')
        params = {'username': self.username}
        self.ids['password'].text = ''
        AsyncRequest(url, params=params, on_success=self.populate_fields)

    def populate_fields(self, resp):
        self.data = resp.json()[0]
        for key in self.data:
            if key == 'permissions':
                continue
            self.ids[key].text = self.data[key]

        self.ids['icon_email'].text = self.data['email']

    def update(self):
        if not self.ids['password'].text:
            ErrorPopup('Password field can\'t be empty')
            return
        if ':' in self.ids['password'].text:
            ErrorPopup('Password contains ":"')
            return

        self.data['password'] = tokenize(self.ids['password'].text)
        self.data['email'] = self.ids['email'].text
        url = urlTo('accounts')
        AsyncRequest(url, data=self.data, method='PATCH', on_success=self.update_success)

    def update_success(self, resp):
        self.query_profile()
        SuccessPopup('Profile updated')
