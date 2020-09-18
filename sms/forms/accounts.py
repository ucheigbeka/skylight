import os
from random import choices
from string import digits, ascii_letters
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty, DictProperty

from sms import urlTo, titles
from sms.forms.template import FormTemplate
from sms.forms.signin import tokenize
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import SuccessPopup, ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'accounts.kv')
Builder.load_file(kv_path)

alphanumeric_chars = ascii_letters + digits

permissions = [
    "{\"read\": true, \"write\": true, \"superuser\": true, \"levels\": [100, 200, 300, 400, 500, 600], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [100, 200, 300, 400, 500, 600], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [100], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [200], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [300], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [400], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [500], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": true, \"superuser\": false, \"levels\": [600], \"usernames\": [\"%s\"]}",
    "{\"read\": true, \"write\": false, \"superuser\": false, \"levels\": [100, 200, 300, 400, 500, 600], \"usernames\": [\"%s\"]}"
]

titles_perm = dict(zip(titles, permissions))


def unload():
    Builder.unload_file(kv_path)


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
            if acct['title'] in self.available_titles:
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
        data = {
            'permissions': titles_perm[self.ids['title'].text] % self.ids['username'].text
        }
        data['fullname'] = self.ids['fname'].text + ' ' + self.ids['lname'].text
        data['email'] = self.ids['email'].text
        data['username'] = self.ids['username'].text
        data['title'] = self.ids['title'].text
        data['password'] = tokenize(self.ids['pwd'].text)
        url = urlTo('accounts')
        AsyncRequest(url, method='POST', data=data, on_success=self.success)

    def success(self, resp):
        self.dismiss()
        msg = 'Account successfully created'
        if self.ids['cbox'].active:
            msg += '\nPassword: ' + self.ids['pwd'].text
        SuccessPopup(auto_dismiss=False, message=msg)


class RemoveAccountPopup(Popup):
    def __init__(self, username='', **kwargs):
        super(RemoveAccountPopup, self).__init__(**kwargs)
        self.ids['username'].text = username

    def remove(self):
        params = {'username': self.ids['username'].text}
        url = urlTo('accounts')
        AsyncRequest(url, method='DELETE', params=params, on_success=self.success)

    def success(self, resp):
        self.dismiss()
        msg = 'Account successfully deleted'
        SuccessPopup(message=msg)


class ResetAccountPopup(PopupBase):
    accounts = ListProperty()
    selected_acct = DictProperty()

    def __init__(self, username='', **kwargs):
        super(ResetAccountPopup, self).__init__(**kwargs)
        self.ids['username'].text = username

    def get_user(self, username):
        for acct in self.accounts:
            if acct['username'] == username:
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
        username = self.ids['username'].text
        self.selected_acct = self.get_user(username)
        self.selected_acct['password'] = tokenize(self.ids['pwd'].text)
        url = urlTo('accounts')
        AsyncRequest(url, method='PATCH', data=self.selected_acct, on_success=self.success)

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

    title = 'Accounts'

    def __init__(self, **kwargs):
        super(Accounts, self).__init__(**kwargs)
        self.dv.dv.set_viewclass('DataViewerLabel')

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
        selected_item = self.dv.dv.get_selected_items()
        username = '' if not len(selected_item) else selected_item[0][0]
        rm_acct = RemoveAccountPopup(username=username)
        rm_acct.bind(on_dismiss=self.refresh)
        rm_acct.open()

    def reset_account(self):
        selected_item = self.dv.dv.get_selected_items()
        username = '' if not len(selected_item) else selected_item[0][0]
        reset_acct = ResetAccountPopup(
            username=username, accounts=self.accounts)
        reset_acct.bind(on_dismiss=self.refresh)
        reset_acct.open()

    def refresh(self, *args):
        self.get_accts()
