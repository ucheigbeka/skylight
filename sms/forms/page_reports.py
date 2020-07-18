import os
from kivy.lang import Builder

from sms.forms.template import FormTemplate
from sms.scripts.student_update import StudentUpdatePopup
from sms.scripts.gpa_cards import GpaCardsPopup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'page_reports.kv')
Builder.load_file(kv_path)


class PageReports(FormTemplate):
    def open_student_update_popup(self):
        StudentUpdatePopup().open()

    def open_gpa_cards_popup(self):
        GpaCardsPopup().open()
