import os
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty,\
    DictProperty, BooleanProperty, AliasProperty, ObjectProperty

from sms import urlTo, get_current_session
from sms.forms.template import FormTemplate
from sms.utils.popups import ErrorPopup
from sms.utils.asyncrequest import AsyncRequest

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_registration.kv')
Builder.load_file(kv_path)

# dict of available course codes mapping to a list of its title and credit
FIRST_SEM_COURSES = {}
SECOND_SEM_COURSES = {}

Clock.max_iteration = 4
print(Clock.max_iteration)


class CSpinner(Factory.CustomSpinner):
    root = ObjectProperty(None)
    index = NumericProperty(0)

    # def on_text(self, instance, value):
    #     rv = self.root.dv.ids.rv

    #     if value in FIRST_SEM_COURSES:
    #         course_title, credit = FIRST_SEM_COURSES[value]
    #         del FIRST_SEM_COURSES[value]
    #         course_codes = FIRST_SEM_COURSES.keys()
    #     else:
    #         course_title, credit = SECOND_SEM_COURSES[value]
    #         del SECOND_SEM_COURSES[value]
    #         course_codes = SECOND_SEM_COURSES.keys()

    #     rv._data[self.index][0] = course_title
    #     rv._data[self.index][1] = credit

    #     self.root.course_code_data.append(course_codes)
    #     rv._data.append(['', ''])

    #     self.disabled = True


class CourseRegViewBase(BoxLayout):
    _data = ListProperty()
    course_code_data = ListProperty()
    headers = ListProperty()
    widths = ListProperty()
    prop = DictProperty()
    dv = ObjectProperty(None)

    def generate_course_codes(self):
        data_for_spinner = []
        for index, course_code in enumerate(self.course_code_data):
            prop = {'root': self, 'index': index, 'width': 100}
            if isinstance(self.course_code_data[0], str):
                prop.update(self.prop)
                prop.update({'text': course_code})
            else:
                prop.update({'values': course_code})
            data_for_spinner.append(prop)

        print(data_for_spinner)
        return data_for_spinner

    data_for_spinner = AliasProperty(generate_course_codes, bind=['course_code_data'])


class CourseRegView(BoxLayout):
    compulsory_course_reg_view = ObjectProperty(None)
    compulsory_course_reg_data = ListProperty()
    compulsory_course_code_data = ListProperty()

    regular_course_reg_view = ObjectProperty(None)
    regular_course_reg_data = ListProperty()
    regular_course_code_data = ListProperty()

    def remove_data(self):
        self.regular_course_reg_view.dv.remove_data()
        if len(self.regular_course_code_data) > 1:
            self.regular_course_code_data.pop()
        elif len(self.regular_course_code_data) == 1:
            self.regular_course_code_data = ['']


class CourseRegistration(FormTemplate):
    disable_entries = BooleanProperty(False)
    first_sem_view = ObjectProperty(None)
    second_sem_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CourseRegistration, self).__init__(**kwargs)
        self.ids.reg_session.text = str(get_current_session())

    def search(self):
        url = urlTo('course_reg')
        param = {'mat_no': self.ids.mat_no.text, 'acad_session': self.ids.reg_session.text}
        AsyncRequest(url, on_success=self.populate_fields, on_failure=self.show_error, params=param)

    def populate_fields(self, resp):
        self.disable_entries = True
        data = resp.json()

        # populate personal info fields
        personal_info = data['personal_info']
        self.ids.surname.text = personal_info['surname']
        self.ids.othernames.text = personal_info['othernames']
        self.ids.cur_level.text = personal_info['current_level']
        self.ids.phone_no.text = personal_info['phone_no']
        self.ids.prob_stat.text = self.ids.prob_stat.values[data['probation_status']]

        # populate compulsory courses field
        courses = data['courses']
        comp_first_sem_courses = courses['first_sem']
        comp_second_sem_courses = courses['second_sem']

        for code, title, credit in comp_first_sem_courses:
            self.first_sem_view.compulsory_course_code_data.append(code)
            self.first_sem_view.compulsory_course_reg_data.append([title, credit])
        for code, title, credit in comp_second_sem_courses:
            self.second_sem_view.compulsory_course_code_data.append(code)
            self.second_sem_view.compulsory_course_reg_data.append([title, credit])

        # queues regular courses
        choices = data['choices']
        first_sem_courses = choices['first_sem']
        second_sem_courses = choices['second_sem']

        for code, title, credit in first_sem_courses:
            FIRST_SEM_COURSES[code] = [title, credit]
        for code, title, credit in second_sem_courses:
            SECOND_SEM_COURSES[code] = [title, credit]

        self.first_sem_view.regular_course_reg_data = [['', '']]
        self.first_sem_view.regular_course_code_data = [FIRST_SEM_COURSES.keys()]
        self.second_sem_view.regular_course_reg_data = [['', '']]
        self.second_sem_view.regular_course_code_data = [SECOND_SEM_COURSES.keys()]

    def clear(self):
        global FIRST_SEM_COURSES, SECOND_SEM_COURSES

        self.disable_entries = False
        fields = list(self.ids.keys())
        fields.remove('passport')
        fields.remove('first_sem_view')
        fields.remove('second_sem_view')
        for field in fields:
            self.ids[field].text = ''
        self.ids.reg_session.text = str(get_current_session())
        self.ids.mat_no.text = 'ENG'

        self.first_sem_view.compulsory_course_code_data = []
        self.first_sem_view.compulsory_course_reg_data = []
        self.second_sem_view.compulsory_course_code_data = []
        self.second_sem_view.compulsory_course_reg_data = []

        self.first_sem_view.regular_course_reg_data = [['', '']]
        self.first_sem_view.regular_course_code_data = ['']
        self.second_sem_view.regular_course_reg_data = [['', '']]
        self.second_sem_view.regular_course_code_data = ['']

        FIRST_SEM_COURSES = {}
        SECOND_SEM_COURSES = {}

    def show_error(self, resp):
        ErrorPopup('Record not found')


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
    runTouchApp(CourseRegistration())
