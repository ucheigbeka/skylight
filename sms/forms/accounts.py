import os
from random import choices
from string import digits, ascii_letters
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty, DictProperty

from sms import urlTo
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import SuccessPopup, ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'accounts.kv')
Builder.load_file(kv_path)

alphanumeric_chars = ascii_letters + digits
titles = [
    'Head of department', 'Exam officer', '100 level course adviser',
    '200 level course adviser', '300 level course adviser',
    '400 level course adviser', '500 level course adviser',
    '500 level course adviser(2)', 'Secretary'
]


class PopupBase(Popup):
    def highlight_textinput(self, instance):
        instance.background_color = [1, 0, 0, 1]
        instance.bind(text=self.reset_color)

    def reset_color(self, instance, value):
        instance.background_color = [1, 1, 1, 1]


class NewAccountPopup(PopupBase):
    accounts = ListProperty()
    available_titles = ListProperty(titles)

    def on_open(self, *args):
        for acct in self.accounts:
            self.available_titles.remove(acct['title'])

    def create(self):
        if not self.ids['cbox'].active and self.ids['pwd'].text != self.ids['rpwd'].text:
            self.highlight_textinput(self.ids['pwd'])
            self.highlight_textinput(self.ids['rpwd'])
            return
        if ':' in self.ids['username'].text:
            ErrorPopup(message='Username contains ":"')
            self.highlight_textinput(self.ids['username'])
            return
        elif ':' in self.ids['pwd'].text:
            ErrorPopup(message='Password contains ":"')
            self.highlight_textinput(self.ids['pwd'])
            return
        if self.ids['cbox'].active:
            self.ids['pwd'].text = ''.join(choices(list(alphanumeric_chars), k=10))
        data = {}
        data['firstname'] = self.ids['fname'].text
        data['lastname'] = self.ids['lname'].text
        data['email'] = self.ids['email'].text
        data['username'] = self.ids['username'].text
        data['title'] = self.ids['title'].text
        data['password'] = self.ids['pwd'].text
        url = urlTo('accounts')
        AsyncRequest(url, method='POST', data=data, on_success=self.success)

    def success(self, resp):
        self.dismiss()
        msg = 'Account successfully created'
        if self.ids['cbox'].active:
            msg += '\nPassword: ' + self.ids['pwd'].text
        SuccessPopup(auto_dismiss=False, message=msg)


class RemoveAccountPopup(Popup):
    def remove(self):
        params = {'uid': int(self.ids['uid'].text)}
        url = urlTo('accounts')
        AsyncRequest(url, method='DELETE', params=params, on_success=self.success)

    def success(self, resp):
        self.dismiss()
        msg = 'Account successfully deleted'
        SuccessPopup(message=msg)


class ResetAccountPopup(PopupBase):
    accounts = ListProperty()
    selected_acct = DictProperty()

    def get_user(self, uid):
        for acct in self.accounts:
            if acct['user_id'] == uid:
                return acct

    def reset(self):
        if not self.ids['cbox'].active and self.ids['pwd'].text != self.ids['rpwd'].text:
            self.highlight_textinput(self.ids['pwd'])
            self.highlight_textinput(self.ids['rpwd'])
            return
        if ':' in self.ids['pwd'].text:
            ErrorPopup(message='Password contains ":"')
            self.highlight_textinput(self.ids['pwd'])
            return
        if self.ids['cbox'].active:
            self.ids['pwd'].text = ''.join(choices(list(alphanumeric_chars), k=10))
        uid = int(self.ids['uid'].text)
        self.selected_acct = self.get_user(uid)
        self.selected_acct['password'] = self.ids['pwd'].text
        url = urlTo('accounts')
        AsyncRequest(url, method='PUT', data=self.selected_acct, on_success=self.success)

    def success(self, resp):
        self.dismiss()
        msg = self.selected_acct['username'] + '\'s account has been reset'
        if self.ids['cbox'].active:
            msg += '\nNew password: ' + self.ids['pwd'].text
        SuccessPopup(auto_dismiss=False, message=msg)


class Accounts(FormTemplate):
    dv = ObjectProperty()
    _data = ListProperty()
    accounts = ListProperty()

    def __init__(self, **kwargs):
        super(Accounts, self).__init__(**kwargs)
        self.dv.rv.viewclass = 'DataViewerLabel'

    def get_accts(self):
        url = urlTo('accounts')
        AsyncRequest(url, method='GET', on_success=self.populate_dv, params={})

    def on_enter(self):
        self.get_accts()

    def populate_dv(self, resp):
        data = resp.json()
        fields = [val.lower() for val in self.dv.headers]
        dv_data = []
        for item in data:
            dv_data.append([item[field] for field in fields])
        self._data = dv_data
        self.accounts = data

    def new_account(self):
        new_acct = NewAccountPopup(accounts=self.accounts)
        new_acct.bind(on_dismiss=self.refresh)
        new_acct.open()

    def remove_account(self):
        rm_acct = RemoveAccountPopup()
        rm_acct.bind(on_dismiss=self.refresh)
        rm_acct.open()

    def reset_account(self):
        reset_acct = ResetAccountPopup(accounts=self.accounts)
        reset_acct.bind(on_dismiss=self.refresh)
        reset_acct.open()

    def refresh(self, *args):
        self.get_accts()
