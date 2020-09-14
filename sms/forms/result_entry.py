import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from sms import urlTo, get_current_session, get_assigned_level
from sms.forms.template import FormTemplate
from sms.forms.result_entry_single import insert_extra
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'result_entry.kv')
Builder.load_file(kv_path)

DEFAULT_DV_DATA = [
    ['Completed', ''],
    ['Outstanding', ''],
    ['No. of students', '']
]


class ResultEntry(FormTemplate):
    title = 'Result Entry'
    dv = ObjectProperty()
    dv2 = ObjectProperty()

    def __init__(self, **kwargs):
        super(ResultEntry, self).__init__(**kwargs)
        self.dv2.dv.set_viewclass('DataViewerLabel')
        self.dv2.dv.bind(selected_indexes=self.open_in_singles_screen)

    def on_enter(self, *args):
        self.persist_data = False

    def setup(self):
        self.data = []
        self.query_params = {}
        self.selected_indexes = []
        self.ids['session'].text = str(get_current_session())
        assigned_level = get_assigned_level()
        self.ids['level'].text = '' if not assigned_level else str(assigned_level)
        self.dv2.dv._data = [[''] * self.dv2.cols]
        self.dv.set_data(DEFAULT_DV_DATA)

    def search(self):
        url = urlTo('results_stats_multiple')
        if self.validate_inputs():
            session = int(self.ids['session'].text)
            level = int(self.ids['level'].text)
            self.query_params = {'acad_session': session, 'level': level}
            AsyncRequest(url, params=self.query_params, on_success=self.populate_fields)
        else:
            ErrorPopup('Fields can\'t be empty')

    def query_results_stats(self, mat_no):
        url = urlTo('results_stats_single')
        params = {'mat_no': mat_no}
        params.update(self.query_params)
        AsyncRequest(url, params=params, on_success=self.refresh_fields)

    def refresh(self):
        self.num_queued_queries = 0
        for idx in self.selected_indexes:
            mat_no = self.data[idx][0]
            self.query_results_stats(mat_no)
            self.num_queued_queries += 1

    def refresh_fields(self, resp):
        data = resp.json()
        index = self.selected_indexes.pop(0)
        self.data[index] = data
        self.num_queued_queries -= 1

        if not self.num_queued_queries:
            self.dv2.dv.set_data(self.data)
            self.populate_stats_fields()

    def compute_stats(self, data):
        num_completed = 0
        num_outsanding = 0
        num_students = 0
        for course_details in data:
            if course_details[2] and course_details[2] == course_details[3]:
                num_completed += 1
            else:
                num_outsanding += 1
            num_students += 1
        return num_completed, num_outsanding, num_students

    def populate_fields(self, resp):
        data = resp.json()
        if data:
            self.data = data
            self.dv2.dv.set_data(data)
            self.populate_stats_fields()
        else:
            self.dv2._data = [[''] * self.dv2.cols]

    def populate_stats_fields(self):
        stats = self.compute_stats(self.data)
        stats_data = [row[:] for row in DEFAULT_DV_DATA]
        for idx in range(len(stats_data)):
            stats_data[idx][1] = str(stats[idx])
        self.dv.set_data(stats_data)

    def open_in_singles_screen(self, instance, value):
        if value:
            data = self.dv2.dv.get_selected_items()[0]
            selected_indexes = self.dv2.dv.selected_indexes[:]
            self.selected_indexes.extend(selected_indexes)
            params = {
                'mat_no': data[0],
                'acad_session': int(self.ids['session'].text)
            }
            insert_extra(params)
            self.persist_data = True
            self.manager.transition.direction = 'left'
            self.manager.current = 'result_entry_single'
            self.dv2.dv.deselect(value[0])

    def clear_fields(self):
        if not self.persist_data:
            super(ResultEntry, self).clear_fields()
