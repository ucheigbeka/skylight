import os
from kivy.lang import Builder
from kivy.uix.popup import Popup

from sms.forms.template import FormTemplate

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'student_update.kv')
Builder.load_file(kv_path)


class StudentUpdatePopup(Popup):
    pass


class StudenUpdateForm(FormTemplate):
    pass
