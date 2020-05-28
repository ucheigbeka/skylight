import kivy
kivy.require('1.7.0')

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from sms import sm


class StudentManagementSystemApp(App):
    title = 'Student Management System'
    icon = 'skylight.png'

    def build(self):
        return sm


if __name__ == '__main__':
    StudentManagementSystemApp().run()
