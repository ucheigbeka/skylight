import kivy
kivy.require('1.7.0')

from kivy.app import App
from sms import sm


class StudentManagementSystemApp(App):
	title = 'Student Management System'

	def build(self):
		return sm


if __name__ == '__main__':
	StudentManagementSystemApp().run()
