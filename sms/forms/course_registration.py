import os
import subprocess
import sys
import json
from copy import deepcopy

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty,\
    ObjectProperty, BooleanProperty, StringProperty

from sms import urlTo, get_current_session, get_assigned_level, root, get_dirs
from sms.forms.template import FormTemplate
from sms.utils.popups import ErrorPopup, YesNoPopup
from sms.utils.asyncrequest import AsyncRequest

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_registration.kv')
Builder.load_file(kv_path)

# dict of available course codes mapping to a list of its title and credit
FIRST_SEM_COURSES = {}
SECOND_SEM_COURSES = {}


def unload():
    Builder.unload_file(kv_path)


class CourseRegView(BoxLayout):
    grid = ObjectProperty()
    fields = ListProperty()
    num_compulsory_courses = NumericProperty()
    course_codes = ListProperty()
    course_details = ListProperty()
    max_sememster_credits = NumericProperty(30)
    total_credits = NumericProperty()
    size_hints = [.35, .5, .15]
    credits_left = 0

    def __init__(self, **kwargs):
        try:
            super(CourseRegView, self).__init__(**kwargs)
        except TypeError:
            super(BoxLayout, self).__init__(**kwargs)
        self.course_code_options = self.course_codes[:]

    def add_field(self, bind_spinner=True):
        if self.credits_left and (self.course_code_options or not bind_spinner):
            course_code_spinner = Factory.CustomSpinner(
                disabled=True,
                size_hint_x=self.size_hints[0])
            if bind_spinner:
                course_code_spinner.disabled = False
                course_code_spinner.values = self.course_code_options
                course_code_spinner.bind(text=self.set_course_details)
            course_title_textinput = Factory.CustomTextInput(
                disabled=True,
                size_hint_x=self.size_hints[1])
            course_credit_textinput = Factory.CustomTextInput(
                disabled=True,
                size_hint_x=self.size_hints[2])

            self.grid.add_widget(course_code_spinner)
            self.grid.add_widget(course_title_textinput)
            self.grid.add_widget(course_credit_textinput)

            self.fields.append([
                course_code_spinner,
                course_title_textinput,
                course_credit_textinput
            ])

    def remove_field(self):
        if len(self.fields) - 1 > self.num_compulsory_courses:
            remove_empty_field = True
            if not self.credits_left:
                remove_empty_field = False
            if not self.course_code_options:
                remove_empty_field = False
            if remove_empty_field:
                empty_field = self.fields.pop()
                for wid in empty_field:
                    self.grid.remove_widget(wid)

            widgets = self.fields.pop()
            course_code = widgets[0].text
            credit = int(widgets[2].text)
            for wid in widgets:
                self.grid.remove_widget(wid)

            idx = self.course_codes.index(course_code)
            self.course_code_options.insert(idx, course_code)
            self.total_credits -= credit
            self.add_field()
            return True

    def remove_all_field(self):
        Clock.schedule_once(self._remove_all_field)

    def _remove_all_field(self, dt):
        while self.remove_field():
            continue

    def clear(self):
        self.total_credits = 0
        self.num_compulsory_courses = 0
        self.fields = []
        self.grid.clear_widgets()
        self.ids['btn_fill'].disabled = True

    def set_course_details(self, instance, value):
        if not value:
            return
        instance.disabled = True
        course_title_textinput = self.fields[-1][1]
        course_credit_textinput = self.fields[-1][2]

        idx = self.course_codes.index(value)
        title, credit = self.course_details[idx]
        if credit > self.credits_left:
            instance.disabled = False
            instance.text = ''
            return
        course_title_textinput.text = title if title else ''
        course_credit_textinput.text = str(credit)
        self.total_credits += credit

        self.course_code_options.remove(value)
        self.add_field()

    def get_courses_for_reg(self):
        courses = [[code_wid.text, title_wid.text, int(credits_wid.text)] for code_wid, title_wid, credits_wid in self.fields if code_wid.text]
        return courses

    def populate_regular_courses(self):
        Clock.schedule_once(self._populate_regular_courses)

    def _populate_regular_courses(self, dt):
        course_codes = self.course_code_options[:]
        for course_code in course_codes:
            course_code_spinner = self.fields[-1][0]
            if course_code_spinner.text:
                break
            course_code_spinner.text = course_code

    def insert_compulsory_courses(self, compulsory_courses):
        self.clear()
        self.num_compulsory_courses = len(compulsory_courses)
        for code, title, credit, _ in compulsory_courses:
            self.add_field(bind_spinner=False)

            course_code_spinner = self.fields[-1][0]
            course_title_textinput = self.fields[-1][1]
            course_credit_textinput = self.fields[-1][2]

            course_code_spinner.text = code
            course_title_textinput.text = title if title else ''
            course_credit_textinput.text = str(credit)

            self.total_credits += credit
        self.add_field()

        if not self.num_compulsory_courses:
            self.ids['btn_fill'].disabled = False

    def on_course_codes(self, instance, value):
        self.course_code_options = self.course_codes[:]


class CourseRegistration(FormTemplate):
    disable_entries = BooleanProperty(False)
    first_sem_view = ObjectProperty(None)
    second_sem_view = ObjectProperty(None)
    credits_to_register = NumericProperty()
    max_credits = NumericProperty()
    is_old_course_reg = BooleanProperty(False)
    credits_left = 0

    print_icon_dir = StringProperty(
        os.path.join(os.path.dirname(__file__), '..', 'utils', 'icons', 'icons8-print-32.png'))

    title = 'Course Registration'

    def __init__(self, **kwargs):
        super(CourseRegistration, self).__init__(**kwargs)
        self.first_sem_view.bind(total_credits=self.set_credits_to_register)
        self.second_sem_view.bind(total_credits=self.set_credits_to_register)

    def setup(self):
        self.ids.mat_no.text = 'ENG'
        self.ids.reg_session.text = str(get_current_session())
        self.data = dict()

        assigned_level = get_assigned_level()
        if assigned_level:
            self.ids['cur_level'].values = [str(assigned_level)]
        else:
            self.ids['cur_level'].values = [str(level) for level in range(100, 900, 100)]

    def set_credits_to_register(self, *args):
        self.credits_to_register = self.first_sem_view.total_credits + self.second_sem_view.total_credits
        self.set_sem_view_credits_left()

    def set_sem_view_credits_left(self):
        self.credits_left = self.max_credits - self.credits_to_register
        self.first_sem_view.credits_left = self.credits_left
        self.second_sem_view.credits_left = self.credits_left

    def search(self):
        acad_session = int(self.ids.reg_session.text)
        url = urlTo('course_reg')
        param = {
            'mat_no': self.ids.mat_no.text,
            'acad_session': acad_session
        }
        AsyncRequest(url, on_success=self.populate_fields_for_old_reg, on_failure=self.check_query_session, params=param)

    def populate_fields(self, resp):
        self.disable_entries = True
        self.is_old_course_reg = False
        data = resp.json()

        # populate personal info fields
        personal_info = data.pop('personal_info')
        self.ids.surname.text = personal_info['surname']
        self.ids.othernames.text = personal_info['othernames']
        self.ids.cur_level.text = str(personal_info['level'])
        self.ids.phone_no.text = personal_info['phone_no']
        self.ids.prob_stat.text = self.ids.prob_stat.values[data['probation_status']]
        self.ids.fees_stat.text = self.ids.fees_stat.values[data['fees_status']]

        regulars = data.pop('regulars')
        carryovers = data.pop('carryovers')

        if 'course_reg_new' not in resp.request.path_url:
            [carryovers[sem].extend(regulars[sem]) for sem in ('first_sem', 'second_sem')]
            regulars = {sem: [] for sem in ('first_sem', 'second_sem')}
        elif (personal_info.get("transfer", 0) == 1) or (data['co_credits'] > data['max_credits']):
            # dont enforce carryover registration
            [carryovers[sem].extend(regulars[sem]) for sem in ('first_sem', 'second_sem')]
            regulars = deepcopy(carryovers)
            carryovers = {sem: [] for sem in ('first_sem', 'second_sem')}

        # queues regular courses
        first_sem_courses = regulars['first_sem']
        second_sem_courses = regulars['second_sem']

        FIRST_SEM_COURSES.clear()
        SECOND_SEM_COURSES.clear()

        if 'course_reg_new' in resp.request.path_url:
            for code, title, credit, _ in first_sem_courses:
                FIRST_SEM_COURSES[code] = [title, credit]
            for code, title, credit, _ in second_sem_courses:
                SECOND_SEM_COURSES[code] = [title, credit]

        self.first_sem_view.course_codes = []
        self.second_sem_view.course_codes = []

        self.first_sem_view.course_codes = FIRST_SEM_COURSES.keys()
        self.first_sem_view.course_details = FIRST_SEM_COURSES.values()
        self.second_sem_view.course_codes = SECOND_SEM_COURSES.keys()
        self.second_sem_view.course_details = SECOND_SEM_COURSES.values()

        self.max_credits = data['max_credits']
        self.set_sem_view_credits_left()

        # populate compulsory courses field
        comp_first_sem_courses = carryovers['first_sem']
        comp_second_sem_courses = carryovers['second_sem']

        Clock.schedule_once(lambda dt: self.first_sem_view.insert_compulsory_courses(comp_first_sem_courses))
        Clock.schedule_once(lambda dt: self.second_sem_view.insert_compulsory_courses(comp_second_sem_courses))

        # self.first_sem_view.insert_compulsory_courses(comp_first_sem_courses)
        # self.second_sem_view.insert_compulsory_courses(comp_second_sem_courses)

        data['mat_no'] = self.ids['mat_no'].text
        self.data = data

    def populate_fields_for_old_reg(self, resp):
        self.populate_fields(resp)
        acad_session = int(self.ids.reg_session.text)
        if acad_session < get_current_session():
            self.is_old_course_reg = True

    def register_courses(self):
        if not self.data:
            ErrorPopup('Registration error')
            return
        if not self.validate_inputs:
            ErrorPopup('Fees status field is empty')
            return
        self.data['fees_status'] = int(self.ids['fees_stat'].text == 'Paid')
        courses = {
            'first_sem': self.first_sem_view.get_courses_for_reg(),
            'second_sem': self.second_sem_view.get_courses_for_reg()
        }
        self.data['courses'] = courses
        url = urlTo('course_reg')
        params = {'superuser': True} if root.sm.is_admin else None
        AsyncRequest(url, data=self.data, params=params, method='POST', on_failure=self.show_reg_error, on_success=self.clear_fields)

    def delete_course_reg(self):
        YesNoPopup(message='Do you want to delete this course registration?', on_yes=self._delete_course_reg)

    def _delete_course_reg(self):
        if not self.data:
            ErrorPopup('Delete error')
            return
        params = {
            'mat_no': self.data['mat_no'],
            'acad_session': self.data['course_reg_session'],
            'superuser': True if root.sm.is_admin else None
        }
        url = urlTo('course_reg')
        AsyncRequest(url, params=params, method='DELETE', on_failure=self.show_error, on_success=self.clear_fields)

    def clear_fields(self, *args):
        global FIRST_SEM_COURSES, SECOND_SEM_COURSES
        super(CourseRegistration, self).clear_fields()

        self.disable_entries = False
        self.first_sem_view.clear()
        self.second_sem_view.clear()
        self.max_credits = 0
        self.credits_left = 0
        self.set_sem_view_credits_left()
        self.is_old_course_reg = False

        FIRST_SEM_COURSES = {}
        SECOND_SEM_COURSES = {}

    def check_query_session(self, resp):
        acad_session = int(self.ids.reg_session.text)
        if acad_session == get_current_session():
            url = urlTo('course_reg_new')
            param = {
                'mat_no': self.ids.mat_no.text
            }
            AsyncRequest(url, on_success=self.populate_fields, on_failure=self.show_error, params=param)
        else:
            self.show_error(resp)

    def show_error(self, resp):
        try:
            error = ': ' + resp.json()
        except json.decoder.JSONDecodeError:
            error = ''
        ErrorPopup('Record not found' + error)

    def show_reg_error(self, resp):
        ErrorPopup('Error registering courses: ' + resp.json())

    def generate_course_form(self):
        url = urlTo('course_form')
        try:
            params = {
                'mat_no': self.ids['mat_no'].text,
                'session': int(self.ids['reg_session'].text),
                'to_print': True
            }
        except ValueError:
            ErrorPopup('Fields cannot be empty')
            return
        AsyncRequest(url, params=params, method='GET', on_success=self.print_course_form)

    def print_course_form(self, resp):
        attachment = resp.headers['Content-Disposition']
        filename = attachment[attachment.find('=') + 1:]
        filepath = os.path.join(get_dirs('CACHE_DIR'), filename)
        with open(filepath, 'wb') as fd:
            fd.write(resp.content)
        self.print_pdf(filepath)

    def print_pdf(self, filepath):
        cwd = os.getcwd()
        os.chdir(os.path.expanduser('~'))
        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
                # try:
                #     os.startfile(filepath, 'print')
                # except OSError:
                #     os.startfile(filepath)
            else:
                subprocess.run(['xdg-open', filepath])
        except:
            ErrorPopup(f'Error trying to print {filepath}\nOS currently not supported')

        os.chdir(cwd)
