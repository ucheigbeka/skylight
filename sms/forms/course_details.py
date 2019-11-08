import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_details.kv')
Builder.load_file(kv_path)


class CourseDetails(Screen):
    form_root = form_root

    def search(self, *args):
        pass

    def clear_fields(self, *args):
        for field in self.ids.keys():
            self.ids[field].text = ''


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
