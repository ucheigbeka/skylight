import os
from math import copysign
from time import localtime, asctime, time
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, AliasProperty,\
    NumericProperty

from sms import get_log
from sms.forms.template import FormTemplate
from sms.utils.dataview import DataViewerLabel


form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'logs.kv')
Builder.load_file(kv_path)


class CustomDataViewerLabel(DataViewerLabel):
    textview = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.textview.text = self.text


class Logs(FormTemplate):
    logs = ListProperty()
    ufmt_displayed_logs = ListProperty()    # unformatted displayed logs
    scroll = NumericProperty()
    view_start = NumericProperty(1)
    view_stop = NumericProperty(1)
    dv = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.view_start = 1
        self.view_stop = 1
        super(Logs, self).__init__(**kwargs)
        CustomDataViewerLabel.textview = self.ids['textview']
        self.ufmt_displayed_logs = [['', '', '']]
        self.dv.dv.rv.bind(scroll_y=self.set_scroll)
        self.prev_scroll = 1
        self.bind(scroll=self.query_more_logs)

    def displayed_logs_getter(self, *args, **kwargs):
        displayed_logs = []
        for log in self.ufmt_displayed_logs:
            if not log[0]:
                return [['', '', '']]
            timestamp = log[-1]
            formatted_time = asctime(localtime(timestamp))
            displayed_logs.append(log[:-1] + [formatted_time])
        return displayed_logs

    def on_enter(self):
        get_log(self.populate_dv, limit=100)
        self.dv.dv.rv.viewclass = 'CustomDataViewerLabel'

    def populate_dv(self, resp):
        logs = resp.json()
        d_logs = []
        for log in logs[::-1]:
            timestamp, action = log
            d_logs.append([action[: action.find(' ')], action, timestamp])
        self.logs = d_logs
        self.ufmt_displayed_logs = self.logs
        self.log_offset = 100
        self.view_stop = [len(self.logs), 16][len(self.logs) > 16]

    def extend_dv(self, resp):
        logs = resp.json()
        if not logs[0]:
            return
        old_disp_log_len = len(self.ufmt_displayed_logs)
        for log in logs[::-1]:
            timestamp, action = log
            self.logs.append([action[: action.find(' ')], action, timestamp])
            self.ufmt_displayed_logs.append([action[: action.find(' ')], action, timestamp])
        self.log_offset += 10
        if self.ids.time_spinner.text == 'Time':
            self.filter_by_time(self.ids.time_spinner, 'All')
        else:
            self.filter_by_time(self.ids.time_spinner, self.ids.time_spinner.text)
        self.dv.dv.rv.scroll_y = 1 - old_disp_log_len / len(self.ufmt_displayed_logs)

    def refresh(self, *args):
        get_log(self.populate_dv, limit=100)
        self.dv.dv.rv.scroll_y = 1

    def query_more_logs(self, *args):
        if args:
            if args[1] < 0.001:
                get_log(self.extend_dv, limit=10, offset=self.log_offset)
        else:
            get_log(self.extend_dv, limit=10, offset=self.log_offset)

    def set_scroll(self, instance, value):
        self.scroll = value
        disp_log_size = len(self.ufmt_displayed_logs)
        diff = self.scroll * disp_log_size
        copysign(diff, (self.prev_scroll - self.scroll))
        self.view_start = int(disp_log_size - diff)
        self.view_stop = self.view_start + 16 if self.view_start + 16 < disp_log_size else disp_log_size
        self.prev_scroll = value

    def t_filter(self, t):
        now = time()
        seven_days_ago = now - 60 * 60 * 24 * t
        self.ufmt_displayed_logs = list(filter(lambda x: x[-1] >= seven_days_ago, self.logs))

    def filter_by_time(self, instance, value):
        # TODU: implement filtering by session
        index = instance.values.index(value)
        if index == 0:
            self.ufmt_displayed_logs = self.logs
            return
        elif index == 3:
            return
        funcs = [0, self.t_filter, self.t_filter, 0]
        args = [0, 7, 30, 0]
        funcs[index](args[index])

    def filter_by_user(self, instance, value):
        pass

    def pan_up(self, *args):
        diff = 16 / len(self.ufmt_displayed_logs)
        if self.dv.dv.rv.scroll_y + diff > 1:
            self.dv.dv.rv.scroll_y = 1
        else:
            self.dv.dv.rv.scroll_y += diff

    def pan_down(self, *args):
        diff = 16 / len(self.ufmt_displayed_logs)
        if self.dv.dv.rv.scroll_y - diff < 0:
            self.dv.dv.rv.scroll_y = 0
        else:
            self.dv.dv.rv.scroll_y -= diff

    displayed_logs = AliasProperty(displayed_logs_getter, bind=['ufmt_displayed_logs'])
