import kivy
kivy.require('1.7.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from utils.dialog import OpenFileDialog

# Startup configurations
Window.maximize()


class CustomTextInput(TextInput):
	def __init__(self, **kwargs):
		super(CustomTextInput, self).__init__(**kwargs)
		self.max_length = None

	def insert_text(self, substring, *args):
		if self.max_length and (len(self.text) == self.max_length):
			return
		super(CustomTextInput, self).insert_text(substring, *args)

	def validate(self, instance):
		if not instance.text:
			instance.background_color = [1, 0, 0, 1]


class ImageButton(ButtonBehavior, Image):
	pass


class PersonalInfo(BoxLayout):
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


class PersonalInfoApp(App):
	title = 'Student Management System'

	def build(self):
		return PersonalInfo()


if __name__ == '__main__':
	PersonalInfoApp().run()
