import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty

from sms import urlTo, get_current_session, get_assigned_level, root
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.dataview import DataViewerInput
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'result_entry_single.kv')
Builder.load_file(kv_path)

grading_rules = {}
category_details = []
EXTRAS = {}


def unload():
    Builder.unload_file(kv_path)


def insert_extra(extra):
    EXTRAS.update(extra)


class CustomDataViewerInput(DataViewerInput):
    def on_focus(self, instance, value):
        if not value:
            score_str = self.text
            grade = ''
            if score_str and (score_str.isdecimal() or (score_str[0] == '-' and score_str[1:].isdecimal())):
                for cutoff in sorted(grading_rules, reverse=True):
                    if 100 >= int(score_str) >= cutoff:
                        grade = grading_rules[cutoff]
                        break
            try:
                grad_view = self.root.get_view_by_cord(self.index, self.col_num + 1)
                grad_view.text = grade if grade else ''  # empty string to avoid errors on None
            except:
                pass


class ResultEntrySingle(FormTemplate):
    title = 'Result Entry'
    first_sem_view = ObjectProperty()
    second_sem_view = ObjectProperty()

    def __init__(self, **kwargs):
        super(ResultEntrySingle, self).__init__(**kwargs)

        self.first_sem_view.set_viewclass(CustomDataViewerInput)
        self.second_sem_view.set_viewclass(CustomDataViewerInput)
        self.ids['category'].bind(text=self.update_category_fields)

    def setup(self):
        self.data = {}
        self.ids['mat_no'].text = 'ENG'
        self.ids['level'].text = str(get_assigned_level() or '')
        self.ids['session'].text = str(get_current_session())
        self.ids['category'].disabled = False
        self.ids['extra_txt'].disabled = False
        self.ids['extra_lbl'].text = 'Remark'

    def on_enter(self, *args):
        self.ids.action.text = self.ids.action.values[0]
        super(ResultEntrySingle, self).on_enter(*args)
        if EXTRAS:
            self.ids['mat_no'].text = EXTRAS.get('mat_no')
            self.ids['session'].text = str(EXTRAS.get('acad_session'))
            self.search()

    def search(self):
        url = urlTo('results_2')
        params = {
            'mat_no': self.ids['mat_no'].text,
            'session': self.ids['session'].text
        }
        AsyncRequest(url, method='GET', params=params, on_success=self.get_grading_rules)

    def get_grading_rules(self, resp):
        self.data = resp.json()
        url = urlTo('grading_rules')
        params = {'acad_session': self.data['personal_info']['session_admitted']}
        AsyncRequest(url, params=params, method='GET', on_success=self.populate_fields)

    def set_grading_rules(self, rules):
        global grading_rules
        grading_rules.clear()

        for rule in rules:
            grading_rules[rule[2]] = rule[0]

    def update_category_fields(self, instance, value):
        if value and category_details:
            cat_dets = list(filter(lambda x: x['category'] == value, category_details))[0]
            self.ids['description'].text = cat_dets['description']
            self.ids['extra_lbl'].text = cat_dets['extra'] if cat_dets['extra'] else 'Remark'

    def populate_fields(self, resp):
        self.set_grading_rules(resp.json())
        parse_unregd = lambda crs: [crs[0], crs[1]+"  --NOT REGISTERED", *crs[2:]]
        sems = ("first_sem", "second_sem")

        # join course lists from regd and unregd
        regulars = self.data["regulars"]
        unregd = {sem: map(parse_unregd, self.data["unregd"][sem]) for sem in sems}
        [self.data.update({sem: regulars[sem] + list(unregd[sem])}) for sem in sems]

        self.ids['name'].text = self.data['personal_info']["surname"] + ", " + self.data['personal_info']["othernames"]
        self.ids['level'].text = str(self.data['level'])
        self.ids['session'].text = str(self.data['session'])
        self.ids['level_gpa'].text = '{:.4f}'.format(self.data['level_gpa'])
        self.ids['cgpa'].text = '{:.4f}'.format(self.data['cgpa'])

        self.first_sem_view.set_data(self.data['first_sem'])
        self.second_sem_view.set_data(self.data['second_sem'])

        params = {'level': self.data['level']}
        AsyncRequest(urlTo('category'), params=params, method='GET', on_success=self.populate_category_fields)

    def populate_category_fields(self, resp):
        global category_details
        category_details = resp.json()
        cat_dets = list(filter(lambda x: x['category'] == self.data['category'], category_details))
        if cat_dets:
            cat_dets = cat_dets[0]
            if not cat_dets['editable']:
                self.ids['category'].disabled = True
                self.ids['extra_txt'].disabled = True
            else:
                self.ids['category'].values = list(
                    map(lambda x: x['category'], filter(lambda x: x['editable'], category_details)))
            self.ids['category'].text = cat_dets['category']
            self.ids['description'].text = cat_dets['description']
            self.ids['extra_lbl'].text = cat_dets['extra'] if cat_dets['extra'] else 'Remark'
        else:
            self.ids['category'].values = list(
                map(lambda x: x['category'], filter(lambda x: x['editable'], category_details)))

    def clear_fields(self, *args):
        global EXTRAS
        super(ResultEntrySingle, self).clear_fields()

        self.first_sem_view._data = []
        self.second_sem_view._data = []
        self.ids.action.text = self.ids.action.values[0]
        EXTRAS = {}

    def compute_diff(self, altered_list, original_list):
        diff = []
        for idx in range(len(original_list)):
            if str(original_list[idx][-2]) != str(altered_list[idx][-2]):
                diff.append(altered_list[idx])
        return diff

    def update(self):
        if not self.data:
            return
        first_sem = self.first_sem_view.get_data(), self.data['first_sem']
        second_sem = self.second_sem_view.get_data(), self.data['second_sem']
        diff = []
        [diff.extend(self.compute_diff(*ls)) for ls in (first_sem, second_sem)]

        result_arr = []
        mat_no = self.data['mat_no']
        session = int(self.ids['session'].text)
        action = self.ids.action.text.lower()

        for course in diff:
            code, score = course[0], course[3]
            result_arr.append([code, session, mat_no, score])

        url = urlTo('results_2')
        params = {"action": action, "many": True}
        # todo update params with catg and level if they change
        AsyncRequest(url, data=result_arr, params=params, method='POST', on_success=self.show_response, on_failure=self.show_response)

    def show_response(self, resp):
        try:
            msgs = resp.json()
        except Exception as e:
            err_msg = "Something went wrong"
        else:
            if msgs is None:
                err_msg = "None"
            elif not msgs:
                err_msg = "Done"
            else:
                idxs, err_msgs = zip(*msgs)
                err_msg = '\n'.join(err_msgs)
        ErrorPopup(err_msg, title='Alert', size_hint=(.4, .5), auto_dismiss=False)
