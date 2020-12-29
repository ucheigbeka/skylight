import os
from threading import Thread
from kivy.lang import Builder
from kivy.uix.popup import Popup

from sms import urlTo, start_loading, stop_loading
from sms.scripts import generate_preview
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
            semester = self.ids['semester'].text == 'First Only'
        except ValueError:
            ErrorPopup('Field cannot be empty')
            return
        params = {'acad_session': acad_session, 'level': level, 'first_sem_only': semester, 'raw_score': raw_score}
        AsyncRequest(url, params=params, on_success=self.generate_broadsheet, on_failure=self.show_error)

    def generate_broadsheet(self, resp):
        start_loading(text='Generating preview...')
        try:
            Thread(target=self._generate_broadsheet, args=(resp,)).start()
        except:
            stop_loading()
            self.show_error(resp)

    def _generate_broadsheet(self, resp):
        from sms import root
        reports = root.sm.get_screen('reports')
        screens = generate_preview(resp)
        acad_session = int(self.ids['acad_session'].text)
        level = int(self.ids['level'].text)
        tab_title = '{}L {} broadsheet'.format(level, acad_session)
        reports.generate_report(screens, tab_title)
        self.dismiss()
        root.sm.current = 'reports'
        stop_loading()

    def show_error(self, resp):
        try:
            msg = resp.text
        except:
            msg = 'Something went wrong'
        ErrorPopup(msg)
