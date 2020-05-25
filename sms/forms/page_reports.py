import os
from kivy.lang import Builder

from sms.forms.template import FormTemplate
from sms.scripts.student_update import StudentUpdatePopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'page_reports.kv')
Builder.load_file(kv_path)


class PageReports(FormTemplate):
    def open_student_update_popup(self, *args):
        StudentUpdatePopup().open()
