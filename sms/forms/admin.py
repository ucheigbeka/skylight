from kivy.lang import Builder

from sms import get_kv_path
from sms.forms.template import FormTemplate

kv_path = get_kv_path('admin')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class Administrator(FormTemplate):
    title = 'Administrator'
