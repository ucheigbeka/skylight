from kivy.lang import Builder

from sms import get_kv_path
from sms.forms.template import FormTemplate
from sms.scripts.broadsheet import BroadsheetPopup
from sms.scripts.student_update import StudentUpdatePopup
from sms.scripts.senate_version import SenateVersionPopup
from sms.scripts.gpa_cards import GpaCardsPopup

kv_path = get_kv_path('page_reports')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class PageReports(FormTemplate):
    title = 'Page Reports'

    def open_broadsheet_popup(self):
        BroadsheetPopup().open()

    def open_student_update_popup(self):
        StudentUpdatePopup().open()

    def open_senate_version_popup(self):
        SenateVersionPopup().open()

    def open_gpa_cards_popup(self):
        GpaCardsPopup().open()
