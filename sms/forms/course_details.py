import os
import json
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from sms import urlTo
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_details.kv')
Builder.load_file(kv_path)


class CourseDetails(Screen):
    form_root = form_root

    def search(self, *args):
        course_code = self.ids['course_code'].text
        params = {'course_code': course_code}
        url = urlTo('course_details')
        AsyncRequest(url, params=params, on_success=self.populate_fields, on_failure=self.show_error)

    def populate_fields(self, resp):
        data = json.loads(resp.json())
        for field in self.ids.keys():
            self.ids[field].text = str(data[field])

    def show_error(self, resp):
        ErrorPopup('Course not found')

    def clear_fields(self, *args):
        for field in self.ids.keys():
            self.ids[field].text = ''


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
