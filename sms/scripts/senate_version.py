import os
from threading import Thread
from kivy.lang import Builder
from kivy.uix.popup import Popup

from sms import urlTo, start_loading, stop_loading
from sms.scripts import generate_preview
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'senate_version.kv')
Builder.load_file(kv_path)


class SenateVersionPopup(Popup):
    def search(self, *args):
        url = urlTo('senate_version')
        try:
            acad_session = int(self.ids['acad_session'].text)
            level = int(self.ids['level'].text)
        except ValueError:
            ErrorPopup('Field cannot be empty')
        params = {'acad_session': acad_session, 'level': level}
        AsyncRequest(url, params=params, on_success=self.generate_senate_version)

    def generate_senate_version(self, resp):
        start_loading(text='Generating preview...')
        Thread(target=self._generate_senate_version, args=(resp,)).start()

    def _generate_senate_version(self, resp):
        from sms import root
        reports = root.sm.get_screen('reports')
        screens = generate_preview(resp)
        acad_session = int(self.ids['acad_session'].text)
        tab_title = '{}/{} senate version'.format(acad_session, acad_session + 1)
        reports.generate_report(screens, tab_title)
        self.dismiss()
        root.sm.current = 'reports'
        stop_loading()

    def show_error(self, resp):
        ErrorPopup('Error generating senate version')
