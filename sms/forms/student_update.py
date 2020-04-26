import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'student_update.kv')
Builder.load_file(kv_path)


class StudentUpdatePopup(Popup):
    pass


class StudenUpdateForm(Screen):
    form_root = form_root


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
    runTouchApp(StudenUpdateForm())
