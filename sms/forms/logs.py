import os
from datetime import datetime
from math import copysign
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, AliasProperty,\
    NumericProperty

from sms import get_log, urlTo, root, username, title
from sms.forms.template import FormTemplate
from sms.utils.dataview import DataViewerLabel
from sms.utils.asyncrequest import AsyncRequest


form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'logs.kv')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


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
        self.log_step = 0
        self.bind(scroll=self.query_more_logs)
        self.users = []
        self.operations = []
        self.filter = {}

    def displayed_logs_getter(self, *args, **kwargs):
        displayed_logs = []
        for log in self.ufmt_displayed_logs:
            if not log[0]:
                return [['', '', '']]
            timestamp = log[-1]
            formatted_time = datetime.fromtimestamp(float(timestamp)).strftime("%a %b %#e, %Y; %#I:%M%p")
            formatted_time = formatted_time.replace('PM', 'pm').replace('AM', 'am').replace('  ', ' ')
            displayed_logs.append(log[:-1] + [formatted_time])
        return displayed_logs if displayed_logs else [['', '', '']]

    def on_enter(self):
        kwargs = {} if (root.sm.is_admin == 1) else {'title': title}
        get_log(self.populate_dv, count=15, **kwargs)
        self.dv.dv.set_viewclass('CustomDataViewerLabel')
        self.ids['operations_spinner'].values = list(operations_mapping.keys())
        self.ids['time_sort_spinner'].values = ['Most Recent First', 'Oldest First']
        self.query_users()

    def populate_dv(self, resp):
        logs = resp.json()
        d_logs = []
        for log in logs:
            timestamp, action, user = log
            d_logs.append([user, action, timestamp])
        self.logs = d_logs
        self.ufmt_displayed_logs = self.logs    # Potentially dangerous
        self.log_step = 1
        self.view_stop = [len(self.logs), 16][len(self.logs) > 16]

    def extend_dv(self, resp):
        logs = resp.json()
        if not (logs and logs[0]):
            return
        old_disp_log_len = len(self.ufmt_displayed_logs)
        for log in logs:
            timestamp, action, user = log
            fmt_log = [user, action, timestamp]
            self.logs.append(fmt_log)
            self.ufmt_displayed_logs.append(fmt_log)
        self.log_step += 1
        scroll_y_val = 1 - old_disp_log_len / len(self.ufmt_displayed_logs)
        if scroll_y_val: self.dv.dv.rv.scroll_y = scroll_y_val

    def fetch_all(self):
        self.filter = {} if (root.sm.is_admin == 1) else {'title': title}
        self.show_logs(reset_filter_text=True)

    def fetch_filtered(self):
        date = self.ids['date_picker'].text
        user_title = self.ids['users_spinner'].text
        operation = self.ids['operations_spinner'].text
        time_sort = self.ids['time_sort_spinner'].text
        self.filter = {'reverse': time_sort == 'Oldest First'}
        if not (root.sm.is_admin == 1): self.filter['title'] = title

        if isinstance(date, str) and len(date.split('/')) == 3:
            self.filter['time'] = datetime.strptime(date, '%d/%m/%Y').timestamp()
        if user_title not in ['Users', 'All']: self.filter['title'] = user_title
        if operation not in ['Operations', '']: self.filter['operation'] = operations_mapping[operation]

        self.show_logs()

    def show_logs(self, reset_filter_text=False):
        self.clear_fields(reset_filter_text)
        get_log(self.populate_dv, count=15, **self.filter)
        self.dv.dv.rv.scroll_y = 1
        self.query_users()

    def query_more_logs(self, *args):
        if args:
            if args[1] < 0.001:
                get_log(self.extend_dv, count=15, step=self.log_step, **self.filter)
        else:
            get_log(self.extend_dv, count=15, step=self.log_step, **self.filter)

    def query_users(self):
        url = urlTo('accounts')
        params = {}
        if root.sm.is_admin == 1:
            AsyncRequest(url, params=params, method='GET', on_success=self.update_users)
        else:
            self.update_users(bypass=True)

    def update_users(self, resp=None, bypass=False):
        data = resp.json() if not bypass else [{'username': username, 'title': title}]
        self.users = [['SYSTEM', 'SYSTEM']]
        for row in data:
            self.users.append([row['username'], row['title']])
        self.ids['users_spinner'].values = [user[1] for user in self.users]

    def set_scroll(self, instance, value):
        self.scroll = value
        disp_log_size = len(self.ufmt_displayed_logs)
        diff = self.scroll * disp_log_size
        copysign(diff, (self.prev_scroll - self.scroll))
        self.view_start = int(disp_log_size - diff)
        self.view_stop = self.view_start + 16 if self.view_start + 16 < disp_log_size else disp_log_size
        self.prev_scroll = value

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

    def clear_fields(self, reset_filter_text=False):
        if reset_filter_text:
            self.ids['date_picker'].text = 'From Date'
            self.ids['users_spinner'].text = 'Users'
            self.ids['operations_spinner'].text = 'Operations'
            self.ids['time_sort_spinner'].text = 'Most Recent First'

        self.ids['textview'].text = ''
        self.ufmt_displayed_logs = [['', '', '']]

    displayed_logs = AliasProperty(
        displayed_logs_getter, bind=['ufmt_displayed_logs'])


operations_mapping = {
    'Login': 'users.login',
    'Logout': 'users.logout',

    'Get/Start Course Reg': 'course_reg_2.get_exp',
    # 'Start Course Registration': 'course_reg.init_new',
    'Register Courses': 'course_reg_2.post_exp',
    'Delete Course Reg': 'course_reg_2.delete',

    'Get Results': 'results_2.get_exp',
    'Add Results': 'results_2.post_exp',

    'Get Personal Info': 'personal_info_2.get_exp',
    'Add Personal Info': 'personal_info_2.post_exp',
    'Edit Personal Info': 'personal_info_2.patch',
    'Delete Personal Info': 'personal_info_2.delete',

    'Get Result Update': 'result_update.get',
    'Get Course Form': 'course_form.get',
    'Get Broad-Sheet': 'broad_sheet.get',
    'Get Senate Version': 'senate_version.get',
    'Get GPA Card': 'gpa_cards.get',

    # 'Get Accounts': 'accounts.get',
    'Create Account': 'accounts.post',
    'Edit Account': 'accounts.patch',
    'Delete Account': 'accounts.delete',

    'Backup Database': 'backups.backup',
    'Restore Backup': 'backups.restore',
    'List Backups': 'backups.get',
    'Delete Backups': 'backups.delete',
    'Download Backups': 'backups.download',

    'Set Result Edit': 'results.set_resultedit',
    'Get Result Entry Stats': 'results.get_multiple_results_stats',

    'Add Course': 'course_details.post',
    'Edit Course': 'course_details.patch',
    'Delete Course': 'course_details.delete',

}

if __name__ == '__main__':
    from kivy.app import runTouchApp

    runTouchApp(Logs())
