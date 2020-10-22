import os
from threading import Thread
from kivy.lang import Builder
from kivy.uix.popup import Popup

from sms import urlTo
from sms.scripts import generate_preview_screens
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'broadsheet.kv')
Builder.load_file(kv_path)


class BroadsheetPopup(Popup):
    def search(self, *args):
        url = urlTo('broad_sheet')
        try:
            acad_session = int(self.ids['acad_session'].text)
            level = int(self.ids['level'].text)
            raw_score = self.ids['raw_score'].text == 'Yes'
        except ValueError:
            ErrorPopup('Field cannot be empty')
            return
        params = {'acad_session': acad_session, 'level': level, 'raw_score': raw_score, 'to_print': True}
        AsyncRequest(url, params=params, on_success=self.generate_broadsheet)

    def generate_broadsheet(self, resp):
        Thread(target=self._generate_broadsheet, args=(resp,)).start()

    def _generate_broadsheet(self, resp):
        from sms import root
        reports = root.sm.get_screen('reports')
        screens = generate_preview_screens(resp)
        acad_session = int(self.ids['acad_session'].text)
        tab_title = '{}/{} broadsheet'.format(acad_session, acad_session + 1)
        reports.generate_report(screens, tab_title)
        self.dismiss()
        root.sm.current = 'reports'

    def show_error(self, resp):
        ErrorPopup('Error generating senete version')
