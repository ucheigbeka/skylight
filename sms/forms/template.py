import os
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import Screen

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'template.kv')
Builder.load_file(kv_path)


class FormTemplate(Screen):
    form_root = form_root
    title = StringProperty('')

    def __init__(self, **kwargs):
        super(FormTemplate, self).__init__(**kwargs)
        self._setup()

    def validate_inputs(self, include=None, exclude=None):
        exclude = exclude if exclude else []
        include = include if include else self.ids
        for _id in include:
            if _id not in exclude and isinstance(self.ids[_id], (TextInput, Spinner)):
                if not self.ids[_id].text:
                    return False
        return True

    def _setup(self):
        if self.manager:
            self.setup()

    def on_manager(self, instance, value):
        if value:
            self.setup()

    def setup(self):
        pass

    def clear_fields(self):
        for _id in self.ids:
            if isinstance(self.ids[_id], (TextInput, Spinner)):
                self.ids[_id].text = ''
        self._setup()

    def on_leave(self):
        self.clear_fields()


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
    runTouchApp(FormTemplate())
