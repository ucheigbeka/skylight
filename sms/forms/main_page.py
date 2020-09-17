from datetime import datetime
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty

from sms import get_log, get_kv_path
from sms.forms.template import FormTemplate

kv_path = get_kv_path('main_page')
Builder.load_file(kv_path)


class MainPage(FormTemplate):
    logs = ListProperty()
    dv = ObjectProperty(None)
    title = 'Home'

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
        for log in logs:
            timestamp, action = log
            formatted_time = datetime.fromtimestamp(float(timestamp)).strftime("%a %b %#e, %Y; %#I:%M%p")
            formatted_time = formatted_time.replace('PM', 'pm').replace('AM', 'am').replace('  ', ' ')
            if len(action) > 35:
                action = action[:35] + '...'
            d_logs.append([action[: action.find(' ')], action, formatted_time])
        self.logs = d_logs
