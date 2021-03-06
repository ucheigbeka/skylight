import os
import sys
import traceback


def start():
    import kivy
    kivy.require('1.7.0')

    from kivy.config import Config

    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.set('kivy', 'exit_on_escape', '0')

    from kivy.app import App
    from sms import root

    class StudentManagementSystemApp(App):
        title = 'Student Management System'
        icon = 'skylight.png'

        def build(self):
            return root

    StudentManagementSystemApp().run()


try:
    prev_log = open(os.path.join(os.path.dirname(__file__), 'logs.txt')).read()
except FileNotFoundError:
    prev_log = ''

try:
    fd = open(os.path.join(os.path.dirname(__file__), 'logs.txt'), 'r+', buffering=1)
except FileNotFoundError:
    fd = open(os.path.join(os.path.dirname(__file__), 'logs.txt'), 'w', buffering=1)

if __name__ == '__main__':
    with fd:
        sys.stderr = fd
        try:
            start()
        except Exception:
            traceback.print_exc(file=fd)

