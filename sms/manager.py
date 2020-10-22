import os
from importlib import reload
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, NoTransition, SlideTransition
from kivy.properties import StringProperty, ListProperty,\
    DictProperty, ObjectProperty, BooleanProperty, NumericProperty

from sms import titles, MODE, stop_loading
from sms.scripts.about import about
from sms.scripts.logout import logout
from sms.utils.menubar import LoginActionView, MainActionView
from sms.utils.popups import YesNoPopup
# from sms.utils.asynctask import run_in_background

base_path = os.path.dirname(__file__)
kv_path = os.path.join(base_path, 'manager.kv')

Builder.load_file(kv_path)


class Manager(ScreenManager):
    is_admin = BooleanProperty(False)
    assigned_level = NumericProperty(0)
    imported_modules = DictProperty()

    forms_dict = DictProperty()
    persistent_screens = ListProperty(['reports', 'main_page'])

    def initialize(self, title):
        if not title:
            return
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
        if MODE == 'DEBUG':
            print('Assigned level:', self.assigned_level)

    def remove_screen(self, name):
        screen = self.sm.get_screen(name)
        self.sm.remove_widget(screen)

    # @run_in_background
    def load_screens(self):
        for name, screen in self.forms_dict.items():
            self.add_widget(screen(name=name))
        stop_loading()

    def import_form(self, form):
        if form in self.imported_modules:
            module = self.imported_modules[form]
            reload(module)
        else:
            exec('from sms.forms import ' + form)
            module = locals()[form]
            self.imported_modules[form] = module
        return module

    def set_screens_for_hod(self):
        logs = self.import_form('logs')
        accounts = self.import_form('accounts')

        self.set_screens_for_exam_officer()
        screens = {
            'logs': logs.Logs,
            'accounts': accounts.Accounts
        }
        self.forms_dict.update(screens)
        self.is_admin = 1

    def set_screens_for_exam_officer(self):
        admin = self.import_form('admin')
        course_management = self.import_form('course_management')

        self.set_screens_for_course_adviser()
        screens = {
            'admin': admin.Administrator,
            'course_mgmt': course_management.CourseManagement
        }
        self.forms_dict.update(screens)
        self.is_admin = 2

    def set_screens_for_course_adviser(self):
        course_registration = self.import_form('course_registration')
        result_entry_menu = self.import_form('result_entry_menu')
        result_entry_single = self.import_form('result_entry_single')
        result_entry_multiple = self.import_form('result_entry_multiple')
        result_entry = self.import_form('result_entry')

        self.set_screens_for_secretary()
        screens = {
            'course_registration': course_registration.CourseRegistration,
            'result_entry_menu': result_entry_menu.ResultEntryMenu,
            'result_entry_single': result_entry_single.ResultEntrySingle,
            'result_entry_multiple': result_entry_multiple.ResultEntryMultiple,
            'result_entry': result_entry.ResultEntry
        }
        self.forms_dict.update(screens)

    def set_screens_for_secretary(self):
        personalinfo = self.import_form('personalinfo')
        course_details = self.import_form('course_details')
        page_reports = self.import_form('page_reports')
        reports = self.import_form('reports')
        profile = self.import_form('profile')
        error = self.import_form('error')

        screens = {
            'personal_info': personalinfo.PersonalInfo,
            'course_details': course_details.CourseDetails,
            'page_reports': page_reports.PageReports,
            'reports': reports.Reports,
            'profile': profile.Profile,
            'error': error.Error
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

        super(Root, self).__init__(**kwargs)

        self.set_menu_view(LoginActionView)
        self.view_ins.title = 'Login'

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
        main_page = self.sm.import_form('main_page')

        main_page = main_page.MainPage(name='main_page')
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
        YesNoPopup(message='Are you sure you want to logout?', on_yes=logout, title='Logout')

    def about(self, instance):
        about()

    def exit(self, instance):
        App.get_running_app().stop()
