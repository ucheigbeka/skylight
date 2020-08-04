from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty, ListProperty, DictProperty, ObjectProperty

from sms import titles, MODE


class Manager(ScreenManager):
    sm = ObjectProperty(None)

    from sms.forms.error import Error

    forms_dict = DictProperty({
        'error': Error
    })
    persistent_screens = ListProperty(['reports', 'main_page', 'signin'])
    title = StringProperty('')

    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)

    def on_title(self, instance, value):
        self.initialize(value)

    def on_current(self, instance, value):
        previous_screen = self.current_screen
        if not self.has_screen(value):
            self.add_widget(self.forms_dict[value](name=value))
        super(Manager, self).on_current(instance, value)
        if previous_screen and previous_screen.name not in self.persistent_screens:
            self.remove_screen(previous_screen.name)

    def initialize(self, title):
        try:
            idx = titles.index(title)
        except ValueError as err:
            if MODE == 'DEBUG':
                idx = 0
            else:
                raise ValueError(str(err))
        funcs = [
            self.set_screens_for_hod,
            self.set_screens_for_exam_officer
        ] + [
            self.set_screens_for_course_adviser
        ] * 6 + [
            self.set_screens_for_secretary
        ]
        funcs[idx]()

    # def switch_screen(self, name, direction):
    #     crr_screen_name = self.current
    #     if self.has_screen(name):
    #         self.transition.direction = direction
    #         self.current = name
    #     else:
    #         self.switch_to(self.forms_dict[name](name=name), direction=direction)
    #     if crr_screen_name not in self.persistent_screens:
    #         self.remove_screen(crr_screen_name)

    def remove_screen(self, name):
        screen = self.get_screen(name)
        self.remove_widget(screen)

    def set_screens_for_hod(self):
        from sms.forms.logs import Logs
        from sms.forms.accounts import Accounts

        self.set_screens_for_exam_officer()
        screens = {
            'logs': Logs,
            'accounts': Accounts
        }
        self.forms_dict.update(screens)

    def set_screens_for_exam_officer(self):
        from sms.forms.admin import Administrator
        from sms.forms.course_management import CourseManagement

        self.set_screens_for_course_adviser()
        screens = {
            'admin': Administrator,
            'course_mgmt': CourseManagement
        }
        self.forms_dict.update(screens)

    def set_screens_for_course_adviser(self):
        from sms.forms.course_registration import CourseRegistration
        from sms.forms.result_entry import Result_Entry

        self.set_screens_for_secretary()
        screens = {
            'course_registration': CourseRegistration,
            'result_entry': Result_Entry
        }
        self.forms_dict.update(screens)

    def set_screens_for_secretary(self):
        from sms.forms.personalinfo import PersonalInfo
        from sms.forms.main_page import MainPage
        from sms.forms.course_details import CourseDetails
        from sms.forms.page_reports import PageReports
        from sms.forms.reports import Reports

        screens = {
            'personal_info': PersonalInfo,
            'main_page': MainPage,
            'course_details': CourseDetails,
            'page_reports': PageReports,
            'reports': Reports
        }
        self.add_widget(Reports(name='reports'))
        self.forms_dict.update(screens)

    def logout(self):
        self.forms_dict = {}
