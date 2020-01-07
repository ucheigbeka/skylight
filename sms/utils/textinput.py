from kivy.lang import Builder
from kivy.uix.textinput import TextInput

Builder.load_string('''
<CustomTextInput>:
	size_hint_x: None
	width: 300
	multiline: False
	write_tab: False
	use_bubble: True
''')


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