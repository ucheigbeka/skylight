from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen

try:
    'Imported as a module'
    import os
    from sms.utils.dialog import OpenFileDialog
except ImportError:
    'Ran as a script'
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.dialog import OpenFileDialog

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
