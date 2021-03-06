import os
from kivy.lang import Builder

from sms.forms.template import FormTemplate

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'error.kv')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class Error(FormTemplate):
    title = 'Error'
