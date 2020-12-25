import os
import json
from datetime import datetime
from math import log

from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, StringProperty, ObjectProperty

from sms import urlTo, get_dirs
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import YesNoPopup, ErrorPopup, SuccessPopup

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
        if callback == 'restore':
            restore_popup = RestoreBackupPopup(backup_name=self.backup_name)
            restore_popup.bind(on_dismiss=self.dismiss)
            restore_popup.open()
        else:
            YesNoPopup(message=f'Do you want to {callback} this backup? \n\n{self.backup_name}',
                       on_yes=getattr(self, callback + '_backup'))

    def download_backup(self):
        url = urlTo('backup_download')
        params = {'backup_name': self.backup_name}
        AsyncRequest(url, method='GET', params=params, on_success=self._download_backup, on_failure=self.show_error)

    def _download_backup(self, resp):
        attachment = resp.headers['Content-Disposition']
        filename = attachment[attachment.find('=') + 1:]
        pdf_content = resp.content
        download_path, safety_download_path = get_download_path(), get_dirs('BACKUP_DIR')
        filepaths = [os.path.join(_dir, filename) for _dir in (download_path, safety_download_path)]
        for filepath in filepaths:
            if not os.path.exists(filepath):
                open(filepath, 'wb').write(pdf_content)
        SuccessPopup('Backup downloaded to ' + get_download_path())
        self.dismiss()

    def delete_backup(self):
        url = urlTo('backups')
        params = {'backup_name': self.backup_name}
        AsyncRequest(url, method='DELETE', params=params, on_success=self.delete_success, on_failure=self.show_error)

    def delete_success(self, resp):
        self.dismiss()
        SuccessPopup('Backup deleted')

    def show_error(self, resp):
        try:
            msg = resp.json()
        except json.decoder.JSONDecodeError:
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
        AsyncRequest(url, method='POST', data=data, on_success=self.success, on_failure=self.show_error)

    def success(self, resp):
        self.dismiss()
        SuccessPopup('Database Backup complete')

    def show_error(self, resp):
        try:
            msg = resp.json()
        except json.decoder.JSONDecodeError:
            msg = 'Something went wrong'
        ErrorPopup(msg)


class RestoreBackupPopup(Popup):
    backup_name = StringProperty()

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'Restore Backup')
        self.backup_name = kwargs.get('backup_name', '')
        self.size_hint = (.3, .4)
        super(RestoreBackupPopup, self).__init__(**kwargs)

    def confirm(self):
        YesNoPopup(message=f'Are you sure you want to restore this backup? \n\n{self.backup_name}',
                   on_yes=self.restore, on_no=self.dismiss)

    def restore(self):
        url = urlTo('backups')
        data = {
            'backup_name': self.backup_name,
            'include_accounts': self.ids['include_accounts'].text == 'Yes',
            'backup_current': self.ids['backup_current'].text == 'Yes',
        }
        AsyncRequest(url, method='PATCH', data=data, on_success=self.success, on_failure=self.show_error)

    def success(self, resp):
        self.dismiss()
        SuccessPopup('Database Backup Restored')

    def show_error(self, resp):
        try:
            msg = resp.json()
        except json.decoder.JSONDecodeError:
            msg = 'Something went wrong'
        ErrorPopup(msg)


# ==========================================================================
#                               UTILS
# ==========================================================================

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


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


if __name__ == '__main__':
    from kivy.app import runTouchApp

    runTouchApp(ActionMenuPopup())
