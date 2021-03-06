import os
from kivy.lang import Builder

from sms import urlTo
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_details.kv')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class CourseDetails(FormTemplate):
    title = 'Course Details'

    def search(self, *args):
        course_code = self.ids['code'].text
        if not course_code:
            ErrorPopup('Input can\'t be empty')
            return
        course_code = course_code[:3].upper() + course_code[3:]
        params = {'course_code': course_code}
        url = urlTo('course_details')
        AsyncRequest(url, params=params, on_success=self.populate_fields, on_failure=self.show_error)

    def populate_fields(self, resp):
        data = resp.json()[0]
        for field in self.ids.keys():
            self.ids[field].text = str(data[field])
        self.ids['end_date'].text = '' if data['end_date'] == 2999 else str(data['end_date'])
        self.ids['options'].text = ['Yes', 'No'][data['options'] == 0]
        self.ids['semester'].text = self.ids['semester'].values[data['semester'] - 1]

    def show_error(self, resp):
        ErrorPopup('Course not found')

    def clear_fields(self, *args):
        for field in self.ids.keys():
            self.ids[field].text = ''
