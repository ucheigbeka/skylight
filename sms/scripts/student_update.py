import os
from threading import Thread
from kivy.lang import Builder
from kivy.uix.popup import Popup

from sms import urlTo
from sms.scripts import generate_preview_screens
from sms.utils.asyncrequest import AsyncRequest

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'student_update.kv')
Builder.load_file(kv_path)


class StudentUpdatePopup(Popup):
    def search(self, *args):
        url = urlTo('result_update')
        mat_no = self.ids['mat_no'].text
        raw_score = self.ids['raw_score'].text == 'Yes'
        params = {'mat_no': mat_no, 'raw_score': raw_score, 'to_print': False}
        AsyncRequest(url, params=params, on_success=self.generate_result_update)

    def generate_result_update(self, resp):
        Thread(target=self._generate_result_update, args=(resp,)).start()

    def _generate_result_update(self, resp):
        from sms import root
        reports = root.sm.get_screen('reports')
        screens = generate_preview_screens(resp)
        tab_title = self.ids['mat_no'].text
        reports.generate_report(screens, tab_title)
        self.dismiss()
        root.sm.current = 'reports'

    def show_error(self, resp):
        pass
