import os
from datetime import datetime
from math import log

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, StringProperty, ObjectProperty

from sms import urlTo
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import YesNoPopup, ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'backups.kv')
Builder.load_file(kv_path)
unit_list = list(zip(['B', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2]))


def unload():
    Builder.unload_file(kv_path)


class Backups(FormTemplate):
    _data = ListProperty()
    dv2 = ObjectProperty()
    title = 'Backups'

    def __init__(self, **kwargs):
        super(Backups, self).__init__(**kwargs)
        self.ids['dv2'].dv.set_viewclass('DataViewerLabel')
        self.ids['dv2'].dv.bind(selected_indexes=self.action_menu_popup)

    def on_enter(self, *args):
        self.refresh()

    def get_backups(self):
        url = urlTo('backups')
        AsyncRequest(url, method='GET', on_success=self.populate_dv)

    def populate_dv(self, resp):
        data = resp.json()
        self.clear_fields()
        self._data = [[r['file_name'], fmt_size(r['file_size']), fmt_time(r['last_modified_time'])] for r in data]

    def action_menu_popup(self, instance, value):
        if value:
            data = self.dv2.dv.get_selected_items()[0]
            action_menu = ActionMenuPopup(backup_name=data[0])
            action_menu.bind(on_dismiss=self.refresh)
            action_menu.open()
            self.dv2.dv.deselect(value[0])

    def backup_popup(self):
        create = CreateBackupPopup()
        create.bind(on_dismiss=self.refresh)
        create.open()

    def refresh(self, *args):
        self.clear_fields()
        self.get_backups()

    def clear_fields(self):
        self._data = [[''] * 3]


class ActionMenuPopup(Popup):
    backup_name = StringProperty()

    def __init__(self, **kwargs):
        self.backup_name = kwargs.get('backup_name', '')
        self.title = kwargs.get('title', self.backup_name)
        self.size_hint = (.3, .4)
        super(ActionMenuPopup, self).__init__(**kwargs)

    def confirm(self, callback):
        callback = callback.lower()
        YesNoPopup(message=f'Do you want to {callback} this backup? \n\n{self.backup_name}',
                   on_yes=getattr(self, callback + '_backup'))

    def download_backup(self):
        url = urlTo('backup_download')
        params = {'backup_names': [self.backup_name]}
        AsyncRequest(url, method='GET', params=params, on_failure=self.show_error)

    def restore_backup(self):
        restore_popup = RestoreBackupPopup(backup_name=self.backup_name)
        restore_popup.open()

    def delete_backup(self):
        url = urlTo('backups')
        params = {'backup_name': self.backup_name}
        AsyncRequest(url, method='DELETE', params=params, on_success=self.dismiss, on_failure=self.show_error)

    def show_error(self, resp):
        try:
            msg = resp.json()
        except:
            msg = 'Something went wrong'
        msg = msg['detail'] if 'detail' in msg else msg
        ErrorPopup(msg)


class CreateBackupPopup(Popup):

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'Create Backup')
        self.size_hint = (.3, .4)
        super(CreateBackupPopup, self).__init__(**kwargs)

    def backup(self):
        url = urlTo('backups')
        data = {'tag': self.ids['tag'].text}
        AsyncRequest(url, method='POST', data=data, on_success=self.dismiss, on_failure=self.show_error)

    def show_error(self, resp):
        try:
            msg = resp.json()
        except:
            msg = 'Something went wrong'
        ErrorPopup(msg)


class RestoreBackupPopup(Popup):
    backup_name = StringProperty()

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'Restore Backup')
        self.backup_name = kwargs.get('backup_name', '')
        self.size_hint = (.3, .4)
        super(RestoreBackupPopup, self).__init__(**kwargs)

    def restore(self):
        url = urlTo('backups')
        data = {
            'backup_name': self.backup_name,
            'include_accounts': self.ids['include_accounts'].text == 'Yes',
            'backup_current': self.ids['backup_current'].text == 'Yes',
        }
        AsyncRequest(url, method='PATCH', data=data, on_success=self.dismiss, on_failure=self.show_error)

    def show_error(self, resp):
        try:
            msg = resp.json()
        except:
            msg = 'Something went wrong'
        ErrorPopup(msg)


def fmt_size(num):
    """Human friendly file size"""
    global unit_list
    if num > 0:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024 ** exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    elif num == 0:
        return '0 B'
    return ''


def fmt_time(timestamp):
    ts = datetime.fromtimestamp(float(timestamp)).strftime("%a %b %#e, %Y; %#I:%M%p")
    return ts.replace('PM', 'pm').replace('AM', 'am').replace('  ', ' ')
