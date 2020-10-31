import os
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, StringProperty

from sms import urlTo, get_current_session
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import SuccessPopup, ErrorPopup, YesNoPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_management.kv')
Builder.load_file(kv_path)

keys = [
    'code', 'title', 'credit',
    'semester', 'teaching_dept',
    'start_date', 'end_date', 'options'
]


def unload():
    Builder.unload_file(kv_path)


class NewCoursePopup(Popup):
    course_details = ListProperty()

    def on_open(self, *args):
        course_level = self.course_details[0]['level']
        self.ids['level'].text = str(course_level)

    def add(self):
        try:
            data = {}
            for key in keys[:-3]:
                data[key] = self.ids[key].text
            data['credit'] = int(data['credit'])
            data['semester'] = [1, 2][data['semester'].strip().lower() == 'second']
            data['level'] = int(self.ids['level'].text)
            data['start_date'] = get_current_session() + 1
            data['end_date'] = 2999
            optional = self.ids['opt_yes'].active
            data['options'] = [0, data['semester']][optional]

            data['code'] = data['code'].upper()
            data['teaching_dept'] = data['teaching_dept'].upper()
            url = urlTo('course_details')
            AsyncRequest(url, method='POST', data=data, on_success=self.success)
        except:
            ErrorPopup('Fields cannot be empty')

    def success(self, resp):
        self.dismiss()
        msg = '{} successfully added'.format(self.ids['code'].text)
        SuccessPopup(message=msg)


class RemoveCoursePopup(Popup):
    course_details = ListProperty()
    course_code = StringProperty()
    action = StringProperty()

    def remove(self):
        course_code = self.ids['code'].text
        for course in self.course_details:
            if course['code'] == course_code:
                self.course_code = course_code
                break
        else:
            msg = '{} not found'.format(self.ids['code'].text)
            ErrorPopup(message=msg)
            return

        self.action = ['disable', 'delete'][self.ids['delete'].text == 'Yes']
        if self.action == 'delete':
            YesNoPopup(f'Are you sure you want to Permanently delete {course_code}?', on_yes=self._remove)
        else:
            self._remove()

    def _remove(self):
        params = {
            'code': self.course_code,
            'action': self.action
        }
        url = urlTo('course_details')
        AsyncRequest(url, method='DELETE', params=params, on_success=self.success)

    def success(self, resp):
        self.dismiss()
        msg = '{} successfully deleted'.format(self.ids['code'].text)
        SuccessPopup(message=msg)


class CourseManagement(FormTemplate):
    _data = ListProperty()
    course_details = ListProperty()
    original__data = ListProperty()

    title = 'Course Management'

    def __init__(self, **kwargs):
        super(CourseManagement, self).__init__(**kwargs)
        self.ids['cbox'].bind(active=self.enable_dv_edit)
        self.ids['dv2'].dv.set_viewclass('DataViewerLabel')

    def on_enter(self, *args):
        self._data = [[''] * 8]

    def enable_dv_edit(self, instance, value):
        if value:
            self.ids['dv2'].dv.set_viewclass('DataViewerInput')
        else:
            self.ids['dv2'].dv.set_viewclass('DataViewerLabel')

    def get_course_details(self):
        if not self.ids['lvl_spinner'].text:
            return
        url = urlTo('course_details')
        course_level = int(self.ids['lvl_spinner'].text[:3])
        use_curr_session = self.ids['session_spinner'].text == 'Current session'
        params = {'level': course_level, 'use_curr_session': use_curr_session}
        AsyncRequest(url, method='GET', params=params, on_success=self.populate_dv)

    def populate_dv(self, resp):
        data = resp.json()
        dv_data = []
        for row in data:
            dv_row = []
            for key in keys[:-2]:
                if key == 'semester':
                    dv_row.append(['First', 'Second'][row[key] - 1])
                    continue
                dv_row.append(row[key])
            dv_row.append([row['end_date'], ''][row['end_date'] == 2999])
            dv_row.append(['Yes', 'No'][row['options'] == 0])
            dv_data.append(dv_row)
        self._data = dv_data
        self.original__data = [row[:] for row in dv_data]
        self.course_details = data

    def add_course(self):
        if not self.ids['lvl_spinner'].text:
            return
        new_course_popup = NewCoursePopup(course_details=self.course_details)
        new_course_popup.bind(on_dismiss=self.refresh)
        new_course_popup.open()

    def remove_course(self):
        if not self.ids['lvl_spinner'].text:
            return
        remove_course_popup = RemoveCoursePopup(course_details=self.course_details)
        remove_course_popup.bind(on_dismiss=self.refresh)
        remove_course_popup.open()

    def update_courses(self):
        url = urlTo('course_details')
        diffs = self.compute_diff()
        if not diffs:
            ErrorPopup(message='Nothing to update')
            return
        data = []
        for row in diffs:
            course = {}
            for idx in range(len(row) - 3):
                course[keys[idx]] = row[idx]
            course['credit'] = int(course['credit'])
            course['semester'] = [1, 2][course['semester'].strip().lower() == 'second']
            course['level'] = int(self.ids['lvl_spinner'].text[:3])
            course['start_date'] = row[keys.index('start_date')]
            course['end_date'] = 2999 if not row[keys.index('end_date')] else row[keys.index('end_date')]
            course['options'] = [0, course['semester']][row[keys.index('options')] == 'Yes']

            data['code'] = data['code'].upper()
            data['teaching_dept'] = data['teaching_dept'].upper()

            data.append(course)
        AsyncRequest(url, method='PUT', data=data, on_success=self.update_callback)

    def update_callback(self, resp):
        if resp.text:
            err_msg = '\n'.join(resp.json())
            ErrorPopup(err_msg, title='Alert')
        else:
            msg = 'Update successful'
            SuccessPopup(msg)
        self.refresh()

    def compute_diff(self):
        diff = []
        data = self.ids['dv2'].dv.get_data()
        for idx in range(len(data)):
            if data[idx] != self.original__data[idx]:
                diff.append(data[idx])
        return diff

    def refresh(self, *args):
        self.get_course_details()

    def clear_fields(self):
        self.on_enter()
        self.ids['lvl_spinner'].text = ''
        self.ids['session_spinner'].text = 'Current session'
        self.ids['cbox'].active = False
