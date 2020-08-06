import os
from kivy.lang import Builder
from kivy.core.window import Window

# Backend config
base_url = 'http://127.0.0.1:1807/api/'
# base_url = 'http://ucheigbeka.pythonanywhere.com/api/'

# Frontend config
MODE = 'DEBUG'
token, title = '', ''
kv_surfix = ''

titles = [
    'Head of Department', 'Exam officer', '100 level course adviser',
    '200 level course adviser', '300 level course adviser',
    '400 level course adviser', '500 level course adviser',
    '500 level course adviser(2)', 'Secretary'
]


def urlTo(path):
    return base_url + path


def get_current_session():
    return 2019


def get_token():
    return token


def store_token(_token):
    global token
    token = _token


def set_title(_title):
    global title, kv_surfix
    title = _title
    set_suffix()


def set_suffix():
    global kv_surfix
    try:
        idx = titles.index(title)
    except ValueError:
        if MODE == 'DEBUG':
            idx = 0
        else:
            raise
    idx = 2 if idx in range(2, 8) else idx
    surfixes = {
        0: '.kv',
        1: '_eo.kv',
        2: '_ca.kv',
        8: '_sec.kv'
    }
    kv_surfix = surfixes[idx]


def get_kv_path(fname):
    root = os.path.dirname(__file__)
    fpath_base = os.path.join(root, 'forms', 'kv_container')
    if kv_surfix == '.kv':
        return os.path.join(fpath_base, fname + kv_surfix)
    else:
        return os.path.join(fpath_base, 'variants', fname, fname + kv_surfix)


from sms.utils.asyncrequest import AsyncRequest


def get_log(func, limit=20, offset=0):
    url = urlTo('logs')
    AsyncRequest(url, params={'limit': limit, 'offset': offset}, on_success=func)


# Loads all the kv imports
imports_path = os.path.join(os.path.dirname(
    __file__), 'forms', 'kv_container', 'imports.kv')
Builder.load_file(imports_path)

# Sets the window's mininum size
Window.maximize()
win_size = Window.size
Window.minimum_width = win_size[0] * .7
Window.minimum_height = win_size[1] * .8

from sms.manager import Root

root = Root()

# Load the forms
# from sms.forms.error import Error
# from sms.forms.signin import SigninWindow
# from sms.forms.main_page import MainPage
# from sms.forms.personalinfo import PersonalInfo
# from sms.forms.course_details import CourseDetails
# from sms.forms.page_reports import PageReports
# from sms.forms.course_registration import CourseRegistration
# from sms.forms.result_entry import Result_Entry
# from sms.forms.admin import Administrator
# from sms.forms.logs import Logs
# from sms.forms.reports import Reports
# from sms.forms.accounts import Accounts
# from sms.forms.course_management import CourseManagement

# sm = ScreenManager()
# sign_in = SigninWindow(name='signin')
# main_page = MainPage(name='main_page')
# personal_info = PersonalInfo(name='personal_info')
# course_details = CourseDetails(name='course_details')
# course_reg = CourseRegistration(name='course_registration')
# reports = Reports(name='reports')
# page_reports = PageReports(name='page_reports')
# error = Error(name='error')
# admin = Administrator(name="admin")
# result_entry = Result_Entry(name='result_entry')
# logs = Logs(name="logs")
# accounts = Accounts(name='accounts')
# course_mgmt = CourseManagement(name='course_mgmt')

# Adds the screens in the order that they would appear
# sm.add_widget(sign_in)
# sm.add_widget(main_page)
# sm.add_widget(personal_info)
# sm.add_widget(course_details)
# sm.add_widget(course_reg)
# sm.add_widget(result_entry)
# sm.add_widget(page_reports)
# sm.add_widget(error)
# sm.add_widget(admin)
# sm.add_widget(logs)
# sm.add_widget(reports)
# sm.add_widget(accounts)
# sm.add_widget(course_mgmt)
