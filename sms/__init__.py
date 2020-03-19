import os
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

# Backend config
base_url = 'http://127.0.0.1:1807/api/'
token = ''


def urlTo(path):
    return base_url + path


def get_token():
    return token


def store_token(_token):
    global token
    token = _token


# Loads all the kv imports
imports_path = os.path.join(os.path.dirname(
    __file__), 'forms', 'kv_container', 'imports.kv')
Builder.load_file(imports_path)

# Sets the window's mininum size
Window.maximize()
win_size = Window.size
Window.minimum_width = win_size[0] * .7
Window.minimum_height = win_size[1] * .8

# Load the forms
from sms.forms.error import Error
from sms.forms.signin import SigninWindow
from sms.forms.main_page import MainPage
from sms.forms.personalinfo import PersonalInfo
from sms.forms.course_details import CourseDetails
from sms.forms.page_reports import Reports
from sms.forms.course_registration import CourseRegistration
from sms.forms.admin import Administrator
from sms.forms.admin_page import Admin_Page  # todo: check this
from sms.forms.result_entry import Result_Entry
from sms.forms.student_update import Student_Update
from sms.forms.logs import Logs

sm = ScreenManager()
sign_in = SigninWindow(name='signin')
main_page = MainPage(name='main_page')
personal_info = PersonalInfo(name='personal_info')
course_details = CourseDetails(name='course_details')
course_reg = CourseRegistration(name='course_registration')
page_reports = Reports(name='page_reports')
error = Error(name='error')
admin = Administrator(name="admin")
admin_page = Admin_Page(name='admin_page')  # todo: check this
result_entry = Result_Entry(name='result_entry')
student_update = Student_Update(name='student_update')
logs = Logs(name="logs")

# Adds the screens in the order that they would appear
sm.add_widget(sign_in)
sm.add_widget(main_page)
sm.add_widget(personal_info)
sm.add_widget(course_details)
sm.add_widget(course_reg)
sm.add_widget(student_update)
sm.add_widget(result_entry)
sm.add_widget(page_reports)
sm.add_widget(error)
sm.add_widget(admin)
sm.add_widget(admin_page)  # todo: check this
sm.add_widget(logs)
