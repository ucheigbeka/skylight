import os
from kivy.lang import Builder
from kivy.properties import StringProperty

from sms import urlTo
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup

from sms.forms.personalinfo import insert_extra as func_pi

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'student_summary.kv')
Builder.load_file(kv_path)

MODES_OF_ENTRY = ['PUTME', 'DE (200)', 'DE (300)']


def unload():
    Builder.unload_file(kv_path)


class StudentSummary(FormTemplate):
    title = 'Student Summary'
    profile_icon = StringProperty(os.path.join(
        form_root, 'resc', 'icons', 'icons8-edit-profile-480.png'))

    def setup(self):
        self.ids.passport.source = self.profile_icon

    def search(self, *args):
        url = urlTo('student_summary')
        mat_no = self.ids.mat_no.text
        surname = self.ids.surname_.text
        if mat_no:
            param = {'mat_no': mat_no}
            AsyncRequest(url, on_success=self.populate_personal_info, on_failure=self.show_error, params=param)
        else:
            self.show_error("Feature not implemented yet")

    def populate_personal_info(self, resp):
        data = resp.json()
        self.ids.surname.text = data['surname']
        self.ids.othernames.text = data['othernames']
        self.ids.session_admit.text = str(data['session_admitted'])
        self.ids.mode_of_entry.text = MODES_OF_ENTRY[data['mode_of_entry'] - 1]
        self.ids.curr_level.text = str(data['level'])
        self.ids.sex.text = self.ids.sex.values[data['sex'] != 'M']
        self.ids.phone_no.text = str(data['phone_no'])
        self.ids.grad_status.text = self.ids.grad_status.values[not bool(data['grad_status'])]

    def open_pi_screen(self, screen, params):
        funcs = {
            'personal_info': func_pi
            # TODO: add others
        }
        mat_no = self.ids.mat_no
        if not mat_no:
            self.show_error('No data supplied')
            return
        funcs[screen](params)
        self.persist_data = True
        self.manager.current = screen

    def show_error(self, msg):
        ErrorPopup(message=msg, title=self.title)

    def clear_fields(self):
        if not self.persist_data:
            super(StudentSummary, self).clear_fields()


if __name__ == '__main__':
    from kivy.app import runTouchApp
    runTouchApp(StudentSummary())
