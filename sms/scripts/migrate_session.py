import os

from kivy.lang import Builder
from kivy.uix.popup import Popup

from sms import urlTo, start_loading, stop_loading
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import SuccessPopup, ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'migrate_session.kv')
Builder.load_file(kv_path)


class SessionMigrationPopup(Popup):
    def migrate(self):
        url = urlTo('migrate_session')
        start_loading('Migrating session')
        AsyncRequest(url, method='POST', on_success=self.show_success_popup, on_failure=self.show_error)
        self.dismiss()

    def show_success_popup(self, resp):
        stop_loading()
        SuccessPopup('Migration complete. Restart the program now')

    def show_error(self, resp):
        stop_loading()
        ErrorPopup('Something went wrong')
