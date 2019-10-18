import os
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'page_reports.kv')
Builder.load_file(kv_path)

# Startup configurations
win_size = Window.size


class Reports(Screen):
    form_root = form_root
    win_size = win_size


if __name__ == '__main__':
    from kivy.app import runTouchApp

    runTouchApp(Reports())
