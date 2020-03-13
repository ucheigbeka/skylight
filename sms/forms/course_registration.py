import os
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'course_registration.kv')
Builder.load_file(kv_path)


class RegistrationGrid(BoxLayout):
	col_widths = ListProperty([100, 300, 100])
	# col_widths = ListProperty([80, 300, 100, 50])
	heading = StringProperty('')
	def __init__(self, heading, **kwargs):
		super(RegistrationGrid, self).__init__(**kwargs)
		self.heading = heading.upper()
		self.wid_list = []
		for row in range(10):
			fields = [Factory.CustomTextInput(width=self.col_widths[0])]
			fields.append(Factory.CustomTextInput(width=self.col_widths[1]))
			fields.append(Factory.CustomTextInput(width=self.col_widths[2]))
			# fields.append(Factory.CustomSpinner(values=['Yes', 'No'], width=self.col_widths[3]))
			for field in fields:
				self.ids['grid'].__self__.add_widget(field)
			self.wid_list.append(fields)


class CourseRegistration(Screen):
	form_root = form_root

	def __init__(self, **kwargs):
		super(CourseRegistration, self).__init__(**kwargs)
		# self.first_sem_course_codes = []
		# first_sem_fields, second_sem_fields = [], []
		# for semester in range(2):
		# 	for row in range(10):
		# 		fields = [Factory.CustomSpinner(values=[], width=80)]
		# 		fields.append(Factory.CustomTextInput())
		# 		fields.append(Factory.CustomTextInput(size_hint_x=None, width=100))
		# 		fields.append(Factory.CustomSpinner(values=['Yes', 'No'], width=50))
		# 		if semester == 1:
		# 			for field in fields:
		# 				self.ids['first_sem_grid'].__self__.add_widget(field)
		# 			first_sem_fields.append(fields)
		# 		else:
		# 			for field in fields:
		# 				self.ids['second_sem_grid'].__self__.add_widget(field)
		# 			second_sem_fields.append(fields)
		first_sem_reg_grid = RegistrationGrid('1st semester')
		second_sem_reg_grid = RegistrationGrid('2nd semester')
		self.ids['box'].__self__.add_widget(first_sem_reg_grid)
		self.ids['box'].__self__.add_widget(second_sem_reg_grid)


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
    runTouchApp(CourseRegistration())
