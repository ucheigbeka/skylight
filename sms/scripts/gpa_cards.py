import os
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty

from sms import urlTo
from sms.utils.asyncrequest import AsyncRequest

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'gpa_cards.kv')
Builder.load_file(kv_path)


class GpaCardsView(Screen):
    data = ListProperty()

    def __init__(self, **kwargs):
        super(GpaCardsView, self).__init__(**kwargs)
        self.ids['dv'].dv.set_viewclass('DataViewerLabel')

    def set_data(self, json_data):
        for student_details in json_data:
            row = [student_details['mat_no']]
            row.append(student_details['name'])
            row.extend(student_details['gpas'])
            row.append(student_details['cgpa'])
            self.data.append(row)


class GpaCardsPopup(Popup):
    def get(self):
        url = urlTo('level_gpa_cards')
        params = {'level': int(self.ids['level'].text)}
        AsyncRequest(url, params=params, on_success=self.show_gpa_cards, on_failure=self.show_error)

    def _show_gpa_cards(self, resp):
        from sms import sm
        reports = sm.get_screen('reports')
        data = resp.json()
        tab_title = self.ids['level'].text + ' Level Gpa Card'
        gpa_cards_view = GpaCardsView()
        gpa_cards_view.set_data(data)
        reports.generate_report([gpa_cards_view], tab_title)
        self.dismiss()
        app = App.get_running_app()
        app.root.current = 'reports'

    def show_gpa_cards(self, resp):
        Clock.schedule_once(lambda dt: self._show_gpa_cards(resp))

    def show_error(self, resp):
        pass
