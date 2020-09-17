import os
from time import sleep
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, NoTransition, SlideTransition
from kivy.properties import StringProperty, ListProperty,\
    DictProperty, ObjectProperty, BooleanProperty, NumericProperty

from sms import titles, MODE, urlTo, AsyncRequest, get_token
from sms.utils.menubar import LoginActionView, MainActionView
from sms.utils.popups import YesNoPopup
# from sms.utils.asynctask import run_in_background

base_path = os.path.dirname(__file__)
kv_path = os.path.join(base_path, 'manager.kv')

Builder.load_file(kv_path)


class Manager(ScreenManager):
    is_admin = BooleanProperty(False)
    assigned_level = NumericProperty(0)

    from sms.forms.error import Error

    forms_dict = DictProperty({
        'error': Error
    })
    persistent_screens = ListProperty(['reports', 'main_page'])

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

        if idx in range(2, 8):
            self.assigned_level = (idx - 1) * 100
        print('Assigned level:', self.assigned_level)

    # def on_current(self, instance, value):
    #     previous_screen = self.sm.current_screen
    #     if not self.sm.has_screen(value):
    #         self.sm.add_widget(self.forms_dict[value](name=value))
    #     self.sm.on_current(instance, value)
    #     if previous_screen and previous_screen.name not in self.persistent_screens:
    #         self.remove_screen(previous_screen.name)

    def remove_screen(self, name):
        screen = self.sm.get_screen(name)
        self.sm.remove_widget(screen)

    # @run_in_background
    def load_screens(self):
        for name, screen in self.forms_dict.items():
            print('Loading screen:', name)
            self.add_widget(screen(name=name))
            # sleep(.1)

    def set_screens_for_hod(self):
        from sms.forms.logs import Logs
        from sms.forms.accounts import Accounts

        self.set_screens_for_exam_officer()
        screens = {
            'logs': Logs,
            'accounts': Accounts
        }
        self.forms_dict.update(screens)
        self.is_admin = 1

    def set_screens_for_exam_officer(self):
        from sms.forms.admin import Administrator
        from sms.forms.course_management import CourseManagement

        self.set_screens_for_course_adviser()
        screens = {
            'admin': Administrator,
            'course_mgmt': CourseManagement
        }
        self.forms_dict.update(screens)
        self.is_admin = 2

    def set_screens_for_course_adviser(self):
        from sms.forms.course_registration import CourseRegistration
        from sms.forms.result_entry_menu import ResultEntryMenu
        from sms.forms.result_entry_single import ResultEntrySingle
        from sms.forms.result_entry_multiple import ResultEntryMultiple
        from sms.forms.result_entry import ResultEntry

        self.set_screens_for_secretary()
        screens = {
            'course_registration': CourseRegistration,
            'result_entry_menu': ResultEntryMenu,
            'result_entry_single': ResultEntrySingle,
            'result_entry_multiple': ResultEntryMultiple,
            'result_entry': ResultEntry
        }
        self.forms_dict.update(screens)

    def set_screens_for_secretary(self):
        from sms.forms.personalinfo import PersonalInfo
        from sms.forms.course_details import CourseDetails
        from sms.forms.page_reports import PageReports
        from sms.forms.reports import Reports
        from sms.forms.profile import Profile

        screens = {
            'personal_info': PersonalInfo,
            'course_details': CourseDetails,
            'page_reports': PageReports,
            'reports': Reports,
            'profile': Profile
        }
        self.forms_dict.update(screens)


class Root(BoxLayout):
    menu_bar = ObjectProperty(None)
    sm = ObjectProperty(None)
    view_ins = ObjectProperty(None)
    title = StringProperty('')
    screen_names = ListProperty()

    def __init__(self, **kwargs):
        from sms.forms.signin import SigninWindow
        # from sms.forms.result_entry import ResultEntry

        super(Root, self).__init__(**kwargs)

        self.set_menu_view(LoginActionView)
        self.view_ins.title = 'Login'

        # self.sm.add_widget(ResultEntry(name='r'))
        self.sm.add_widget(SigninWindow(name='signin'))
        self.sm.bind(current=self.set_menu_title)

    def on_title(self, instance, value):
        self.sm.initialize(value)

    def bind_callbacks_for_menu_view(self):
        # Check if callback is already bounded
        if isinstance(self.view_ins, LoginActionView):
            self.view_ins.bind(on_exit_btn_pressed=self.exit)
            self.view_ins.bind(on_previous_btn_pressed=self.about)
        else:
            self.view_ins.bind(on_previous_btn_pressed=self.goto_previous_screen)
            self.view_ins.bind(on_home_btn_pressed=self.home)
            self.view_ins.bind(on_reports_btn_pressed=self.reports)
            self.view_ins.bind(on_settings_btn_pressed=self.settings)
            self.view_ins.bind(on_notification_btn_pressed=self.notification)
            self.view_ins.bind(on_profile_btn_pressed=self.profile)
            self.view_ins.bind(on_logout_btn_pressed=self.logout)

    def set_menu_title(self, instance, value):
        if isinstance(self.view_ins, MainActionView):
            screen = self.sm.get_screen(value)
            self.view_ins.title = screen.title
            self.screen_names.append(value)
            self.view_ins.with_previous = value != 'main_page'

    def set_menu_view(self, view):
        if self.view_ins:
            self.menu_bar.remove_widget(self.view_ins)
        self.view_ins = view()
        self.bind_callbacks_for_menu_view()
        self.menu_bar.add_widget(self.view_ins)

    def switch_screen(self, name):
        self.sm.transition = NoTransition()
        self.sm.current = name
        self.sm.transition = SlideTransition()

    def goto_previous_screen(self, instance):
        if len(self.screen_names) == 1:    # main_page
            self.about(instance)
        else:
            self.screen_names.pop()
            screen_name = self.sm.get_screen(self.screen_names.pop()).name
            self.sm.transition.direction = 'right'
            self.sm.current = screen_name

    def login(self, dt):
        from sms.forms.main_page import MainPage

        main_page = MainPage(name='main_page')
        self.sm.add_widget(main_page)

        self.set_menu_view(MainActionView)
        self.sm.transition.direction = 'left'
        self.sm.current = 'main_page'

        self.sm.load_screens()

    def home(self, instance):
        self.switch_screen('main_page')

    def reports(self, instance):
        self.switch_screen('reports')

    def settings(self, instance):
        return

    def notification(self, instance):
        return

    def profile(self, instance):
        self.switch_screen('profile')

    def logout(self, instance):
        YesNoPopup(message='Do you want to Log out?', on_yes=self.logout_routine)

    def logout_routine(self):
        url = urlTo('logout')
        data = {'token': get_token()}
        AsyncRequest(url, method='POST', data=data)
        self.set_menu_view(LoginActionView)
        self.view_ins.title = 'Login'
        self.sm.forms_dict = {}
        self.switch_screen('signin')

    def about(self, instance):
        pass

    def exit(self, instance):
        App.get_running_app().stop()
