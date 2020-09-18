import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from sms import urlTo, get_current_session, get_assigned_level
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.dataview import DataViewerInput

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'result_entry_single.kv')
Builder.load_file(kv_path)

grading_rules = {}
EXTRAS = {}


def unload():
    Builder.unload_file(kv_path)


def insert_extra(extra):
    EXTRAS.update(extra)


class CustomDataViewerInput(DataViewerInput):
    def on_focus(self, instance, value):
        if not value:
            string = self.text
            if string and string.isdecimal():
                score = int(string)
                grade = 'F'

                for lower_limit in sorted(grading_rules):
                    if score < lower_limit:
                        break
                    grade = grading_rules[lower_limit]
            else:
                grade = ''

            grad_view = self.root.get_view_by_cord(self.index, self.col_num + 1)
            grad_view.text = grade


class ResultEntrySingle(FormTemplate):
    title = 'Result Entry'
    results_view = ObjectProperty()
    carryovers_result_view = ObjectProperty()

    def __init__(self, **kwargs):
        super(ResultEntrySingle, self).__init__(**kwargs)

        self.results_view.set_viewclass(CustomDataViewerInput)
        self.carryovers_result_view.set_viewclass(CustomDataViewerInput)

    def setup(self):
        self.data = []
        self.ids['mat_no'].text = 'ENG'
        assigned_level = get_assigned_level()
        self.ids['level'].text = '' if not assigned_level else str(assigned_level)
        self.ids['session'].text = str(get_current_session())

    def on_enter(self, *args):
        super(ResultEntrySingle, self).on_enter(*args)
        if EXTRAS:
            self.ids['mat_no'].text = EXTRAS.get('mat_no')
            self.ids['session'].text = str(EXTRAS.get('acad_session'))
            self.search()

    def search(self):
        url = urlTo('results_single')
        session = get_current_session() if not self.ids['session'].text else int(self.ids['session'].text)
        params = {
            'mat_no': self.ids['mat_no'].text,
            'acad_session': session
        }
        AsyncRequest(url, method='GET', params=params, on_success=self.get_grading_rules)

    def get_grading_rules(self, resp):
        data = resp.json()
        self.data = data

        url = urlTo('grading_rules')
        session = get_current_session() if not self.ids['session'].text else int(self.ids['session'].text)
        params = {'acad_session': session}
        AsyncRequest(url, params=params, method='GET', on_success=self.populate_fields)

    def set_grading_rules(self, rules):
        global grading_rules
        grading_rules.clear()

        for rule in rules:
            grading_rules[rule[2]] = rule[0]

    def populate_fields(self, resp):
        self.set_grading_rules(resp.json())

        self.ids['name'].text = self.data['name']
        self.ids['level'].text = str(self.data['level'])
        self.ids['session'].text = str(self.data['session'])

        results = self.data['result']
        carryovers = self.data['carryovers']

        self.results_view.set_data(results)
        self.carryovers_result_view.set_data(carryovers)

    def clear_fields(self, *args):
        global EXTRAS
        super(ResultEntrySingle, self).clear_fields()

        self.results_view._data = []
        self.carryovers_result_view._data = []
        EXTRAS = {}

    def compute_diff(self, altered_list, original_list):
        diff = []
        for idx in range(len(original_list)):
            if str(original_list[idx][-2]) != str(altered_list[idx][-2]):
                diff.append(altered_list[idx])
        return diff

    def update(self):
        results_list = self.results_view.get_data()
        carryovers_list = self.carryovers_result_view.get_data()

        if not self.data:
            return

        results_diff = self.compute_diff(results_list, self.data['result'])
        carryovers_diff = self.compute_diff(carryovers_list, self.data['carryovers'])

        data = []
        session = int(self.ids['session'].text)

        for course_list in results_diff:
            course_code = course_list[0]
            score = course_list[-2]
            data.append([course_code, session, self.data['mat_no'], score])

        for course_list in carryovers_diff:
            course_code = course_list[0]
            score = course_list[-2]
            data.append([course_code, session, self.data['mat_no'], score])

        url = urlTo('results')
        if session == get_current_session():
            AsyncRequest(url, data=data, method='POST', on_success=self.clear_fields)
        else:
            AsyncRequest(url, data=data, method='PUT', on_success=self.clear_fields)
