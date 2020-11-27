import os
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, DictProperty

from sms import urlTo, get_username
from sms.scripts.logout import reset
from sms.forms.template import FormTemplate
from sms.forms.signin import tokenize
from sms.utils.popups import SuccessPopup, ErrorPopup
from sms.utils.asyncrequest import AsyncRequest

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'handover.kv')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class AuthenticationPopup(Popup):
    data = DictProperty()

    def __init__(self, **kwargs):
        super(AuthenticationPopup, self).__init__(**kwargs)
        self.auto_dismiss = False

    def on_open(self):
        self.ids['username'].text = get_username()
        self.ids['username'].disabled = True

    def confirm(self):
        url = urlTo('handover')
        self.data['old_username'] = self.ids['username'].text
        self.data['old_password'] = tokenize(self.ids['pwd'].text)
        AsyncRequest(url, method='POST', data=self.data, on_success=self.handover_success)

    def handover_success(self, resp):
        SuccessPopup('Handover successful. Logging out...')
        self.dismiss()
        reset()


class Handover(FormTemplate):
    form_root = form_root
    title = StringProperty('Handover')

    def submit(self):
        if not self.validate_inputs():
            ErrorPopup('Invalid field supplied')
            return
        if self.ids['pwd'].text != self.ids['rpwd'].text:
            self.highlight_textinput(self.ids['pwd'])
            self.highlight_textinput(self.ids['rpwd'])
            return
        if ':' in self.ids['username'].text:
            ErrorPopup(message='Username contains ":"')
            self.highlight_textinput(self.ids['username'])
            return
        if ':' in self.ids['pwd'].text:
            ErrorPopup(message='Password contains ":"')
            self.highlight_textinput(self.ids['pwd'])
            return
        data = {
            'fullname': self.ids['fname'].text + ' ' + self.ids['lname'].text,
            'email': self.ids['email'].text,
            'username': self.ids['username'].text,
            'password': tokenize(self.ids['pwd'].text)
        }
        AuthenticationPopup(data=data).open()

    def highlight_textinput(self, instance):
        instance.background_color = [1, 0, 0, 1]
        instance.bind(text=self.reset_color)

    def reset_color(self, instance, value):
        instance.background_color = [1, 1, 1, 1]
