import os
from time import localtime, asctime
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty

from sms import get_log
from sms.forms.template import FormTemplate

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'main_page.kv')
Builder.load_file(kv_path)


class MainPage(FormTemplate):
    logs = ListProperty()
    dv = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        self.dv.dv.set_viewclass('DataViewerLabel')

    def on_enter(self):
        self.query_logs(0)
        self.event = Clock.schedule_interval(self.query_logs, 30)

    def on_leave(self):
        Clock.unschedule(self.event)
        self.logs = [['', '', '']]

    def query_logs(self, dt):
        get_log(self.populate_dv, limit=10)

    def populate_dv(self, resp):
        logs = resp.json()
        d_logs = []
        for log in logs[::-1]:
            timestamp, action = log
            timestamp = asctime(localtime(timestamp))
            if len(action) > 35:
                action = action[:35] + '...'
            d_logs.append([action[: action.find(' ')], action, timestamp])
        self.logs = d_logs
