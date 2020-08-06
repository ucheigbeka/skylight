import os
from math import copysign
from time import localtime, asctime, time
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, AliasProperty,\
    NumericProperty

from sms import get_log, urlTo
from sms.forms.template import FormTemplate
from sms.utils.dataview import DataViewerLabel
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup


form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'logs.kv')
Builder.load_file(kv_path)

titles_mapping = {
    'All': 0,
    'HOD': 'Head of department',
    'Exam officer': 'Exam officer',
    '100L course adviser': '100 level course adviser',
    '200L course adviser': '200 level course adviser',
    '300L course adviser': '300 level course adviser',
    '400L course adviser': '400 level course adviser',
    '500L course adviser': '500 level course adviser',
    '500L course adviser(2)': '500 level course adviser(2)',
    'Secretary': 'Secretary'
}


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

    title = 'Logs'

    def __init__(self, **kwargs):
        self.view_start = 1
        self.view_stop = 1
        super(Logs, self).__init__(**kwargs)
        CustomDataViewerLabel.textview = self.ids['textview']
        self.ufmt_displayed_logs = [['', '', '']]
        self.dv.dv.rv.bind(scroll_y=self.set_scroll)
        self.prev_scroll = 1
        self.bind(scroll=self.query_more_logs)
        self.users = []
        self.ids['users_spinner'].values = list(titles_mapping.keys())

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
        self.dv.dv.set_viewclass('CustomDataViewerLabel')
        self.query_users()

    def populate_dv(self, resp):
        logs = resp.json()
        d_logs = []
        for log in logs[::-1]:
            timestamp, action = log
            d_logs.append([action[: action.find(' ')], action, timestamp])
        self.logs = d_logs
        self.ufmt_displayed_logs = self.logs    # Potentially dangerous
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
            self.filter_by_time('All')  # (self.ids.time_spinner, 'All')
        else:
            self.filter_log()
        self.dv.dv.rv.scroll_y = 1 - old_disp_log_len / len(self.ufmt_displayed_logs)

    def refresh(self, *args):
        self.clear_fields()
        get_log(self.populate_dv, limit=100)
        self.dv.dv.rv.scroll_y = 1
        self.query_users()

    def query_more_logs(self, *args):
        if args:
            if args[1] < 0.001:
                get_log(self.extend_dv, limit=15, offset=self.log_offset)
        else:
            get_log(self.extend_dv, limit=15, offset=self.log_offset)

    def query_users(self):
        url = urlTo('accounts')
        params = {}
        AsyncRequest(url, params=params, method='GET', on_success=self.update_users)

    def update_users(self, resp):
        data = resp.json()
        for row in data:
            self.users.append([row['username'], row['title']])

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
        time_interval = now - 60 * 60 * 24 * t

        filtered_log = list(
            filter(lambda x: x[-1] >= time_interval, self.logs))

        if filtered_log:
            self.ufmt_displayed_logs = filtered_log
        else:
            self.ufmt_displayed_logs = [['', '', '']]

    def filter_by_time(self, value):
        # TODO: implement filtering by session
        if value == 'Time':
            return

        index = self.ids['time_spinner'].values.index(value)
        if index == 0:
            self.ufmt_displayed_logs = self.logs
            return
        elif index == 3:
            self.ufmt_displayed_logs = self.logs
            return

        funcs = [0, self.t_filter, self.t_filter, 0]
        args = [0, 7, 30, 0]
        funcs[index](args[index])

    def get_user(self, title):
        user = list(filter(lambda user: user[1] == title, self.users))
        return None if not user else list(set(x[0] for x in user))

    def filter_by_user(self, value):
        if value == 'Users' or value == 'All':
            return
        if self.ufmt_displayed_logs[0] == ['', '', '']:
            return

        user = self.get_user(titles_mapping[value])
        if not user:
            msg = 'No active ' + titles_mapping[value].lower()
            ErrorPopup(msg)
            return

        filtered_log = list(
            filter(lambda row: row[0] in user, self.ufmt_displayed_logs))

        if filtered_log:
            self.ufmt_displayed_logs = filtered_log
        else:
            self.ufmt_displayed_logs = [['', '', '']]

    def filter_log(self):
        time_filter_option = self.ids['time_spinner'].text
        users_filter_option = self.ids['users_spinner'].text
        self.filter_by_time(time_filter_option)
        self.filter_by_user(users_filter_option)

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

    def clear_fields(self):
        self.ids['time_spinner'].text = 'Time'
        self.ids['users_spinner'].text = 'Users'
        self.ids['textview'].text = ''
        self.ufmt_displayed_logs = [['', '', '']]

    displayed_logs = AliasProperty(
        displayed_logs_getter, bind=['ufmt_displayed_logs'])
