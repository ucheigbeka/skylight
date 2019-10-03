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
kv_path = os.path.join(form_root, 'kv_container', 'personalinfo.kv')
Builder.load_file(kv_path)

# Startup configurations
Window.maximize()
win_size = Window.size


class PersonalInfo(Screen):
	form_root = form_root
	win_size = win_size

	def add(self, *args):
		''' Code for populating the database'''
		pass

	def cancel(self, *args):
		pass

	def search(self, *args):
		''' Code for querying the database'''
		pass

	def load_image(self, instance, touch):
		if instance.collide_point(*touch.pos) and touch.is_double_tap:
			filter_dict = {'All Picture Files': ['*.png', '*.jpeg', '*.jpg', '*.jpe', '*.jfif'], 'PNG (*.png)': ['*.png'], 
							'JPEG (*.jpeg; *.jpg; *.jpe; *.jfif)': ['*.jpeg', '*.jpg', '*.jpe', '*.jfif'], 
							'All Files': ['*']}
			dialog = OpenFileDialog(filter_dict=filter_dict)
			dialog.bind(on_dismiss=self.render_image)
			dialog.open()

	def render_image(self, instance):
		if instance.selected_path:
			self.ids['passport'].source = instance.selected_path
			self.ids['passport'].allow_stretch = True
			self.ids['passport'].keep_ratio = False


if __name__ == '__main__':
	from kivy.app import runTouchApp

	runTouchApp(PersonalInfo())
