import math
import os
import subprocess
import sys
from copy import deepcopy

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty,\
    ObjectProperty, BooleanProperty, StringProperty

from sms import urlTo, get_current_session, get_assigned_level, get_dirs
from sms.forms.template import FormTemplate
from sms.utils.popups import ErrorPopup, YesNoPopup, SuccessPopup
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
        courses = [code_widget.text for code_widget, _, _ in self.fields if code_widget.text]
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
        for code, title, credit in compulsory_courses:
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
            self.ids['reg_level'].values = [str(assigned_level)]
        else:
            self.ids['reg_level'].values = [str(level) for level in range(100, 900, 100)]

    def set_credits_to_register(self, *args):
        self.credits_to_register = self.first_sem_view.total_credits + self.second_sem_view.total_credits
        self.set_sem_view_credits_left()

    def set_sem_view_credits_left(self):
        # self.credits_left = self.max_credits - self.credits_to_register
        self.credits_left = math.inf
        self.first_sem_view.credits_left = self.credits_left
        self.second_sem_view.credits_left = self.credits_left

    def search(self):
        url = urlTo('course_reg_2')
        reg_lvl_text = self.ids.reg_level.text
        param = {
            'mat_no': self.ids.mat_no.text,
            'session': int(self.ids.reg_session.text),
            'level': int(reg_lvl_text) if reg_lvl_text else None
        }
        AsyncRequest(url, on_success=self.populate_fields, on_failure=self.show_error, params=param)

    def populate_fields(self, resp):
        self.clear_fields()
        self.disable_entries = True
        data = resp.json()

        self.is_old_course_reg = data.get("has_regd") and (data["session"] < get_current_session())

        self.ids.mat_no.text = data["mat_no"] or ''
        self.ids.reg_session.text = str(data["session"]) or ''
        self.ids.fees_stat.text = self.ids.fees_stat.values[data.get('fees_paid', 0)]
        self.ids.reg_level.text = str(data["level"]) or ''

        if data["prev_summary"]:
            plvl, psess, pcatg = data["prev_summary"]
            self.ids.prev_summary.text = f"{psess}/{psess+1} session; {plvl}L; Category: {pcatg}"

            if pcatg not in ["A", "B"]:
                self.ids.prev_summary.background_color = [1, 0.471, 0.306, 1]

        # populate personal info fields
        personal_info = data.pop('personal_info')
        self.ids.surname.text = personal_info['surname'] or ''
        self.ids.othernames.text = personal_info['othernames'] or ''
        self.ids.cur_level.text = str(personal_info['level']) or ''
        self.ids.phone_no.text = personal_info['phone_no'] or ''

        regulars = data.pop('regulars')
        carryovers = {sem: [] for sem in ('first_sem', 'second_sem')}
        carryovers = data.pop('carryovers', carryovers)

        if data.get("has_regd"):
            [carryovers[sem].extend(regulars[sem]) for sem in ('first_sem', 'second_sem')]
            regulars = {sem: [] for sem in ('first_sem', 'second_sem')}
        elif personal_info.get("transfer", 0) == 1:
            # dont enforce carryover registration
            [carryovers[sem].extend(regulars[sem]) for sem in ('first_sem', 'second_sem')]
            regulars = deepcopy(carryovers)
            carryovers = {sem: [] for sem in ('first_sem', 'second_sem')}

        # queues regular courses
        first_sem_courses = regulars['first_sem']
        second_sem_courses = regulars['second_sem']

        FIRST_SEM_COURSES.clear()
        SECOND_SEM_COURSES.clear()

        if not data.get("has_regd"):
            for code, title, credit in first_sem_courses:
                FIRST_SEM_COURSES[code] = [title, credit]
            for code, title, credit in second_sem_courses:
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
        Clock.schedule_once(lambda dt: self.first_sem_view.insert_compulsory_courses(carryovers['first_sem']))
        Clock.schedule_once(lambda dt: self.second_sem_view.insert_compulsory_courses(carryovers['second_sem']))

        self.data = data

    def register_courses(self):
        if self.credits_to_register > self.max_credits:
            YesNoPopup(
                message=f"You're registering {self.credits_to_register}"
                        f" credits which exceeds the allowed maximum of"
                        f" {self.max_credits}. \n\n"
                        f"Do you wish to continue?",
                on_yes=self.register_courses_)
        else:
            self.register_courses_()

    def register_courses_(self):
        if not self.data:
            ErrorPopup('Registration error')
            return
        if not self.validate_inputs:
            ErrorPopup('Fees status field is empty')
            return

        courses = self.first_sem_view.get_courses_for_reg() \
                  + self.second_sem_view.get_courses_for_reg()

        url = urlTo('course_reg_2')
        params = {
            "action": "overwrite",
            "mat_no": self.ids.mat_no.text,
            "session": self.ids.reg_session.text,
            "level": self.ids.reg_level.text,
            "fees_paid": int(self.ids['fees_stat'].text == 'Paid')
        }
        AsyncRequest(url, data=courses, params=params, method='POST', on_failure=self.show_reg_error, on_success=self.resp_on_success)

    def delete_course_reg(self):
        YesNoPopup(message='Do you want to delete this course registration?', on_yes=self._delete_course_reg)

    def _delete_course_reg(self):
        params = {
            "mat_no": self.ids.mat_no.text,
            "session": self.ids.reg_session.text
        }
        url = urlTo('course_reg_2')
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
        self.ids.prev_summary.background_color = [1, 1, 1, 1]

        FIRST_SEM_COURSES = {}
        SECOND_SEM_COURSES = {}

    def show_error(self, resp):
        try:
            error = resp.json()
            if isinstance(error, dict):
                error = error.get("detail", "")
        except Exception as e:
            error = ""
        ErrorPopup(error or "Record not found")

    def show_reg_error(self, resp):
        try:
            message = resp.json()
            if isinstance(message, dict):
                message = message.get("detail", "")
        except Exception as e:
            message = ""
        message = ": " + message if message else ""
        ErrorPopup('Error registering courses' + message)

    def resp_on_success(self, resp):
        SuccessPopup(resp.json())
        self.clear_fields()

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
        # open the file from user home dir to prevent
        # processes left open in program dir
        # This causes problems during OTA upgrade on windows
        cwd = os.getcwd()
        os.chdir(os.path.expanduser('~'))

        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
        except:
            ErrorPopup(f'Error trying to print {filepath}\nOS currently not supported')

        # change back to working dir
        os.chdir(cwd)
