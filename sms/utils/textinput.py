from kivy.uix.textinput import TextInput


class CustomTextInput(TextInput):
	def __init__(self, **kwargs):
		super(CustomTextInput, self).__init__(**kwargs)
		self.max_length = None
		self.multiline = False
		self.size_hint_x = None
		self.width = 300
		self.write_tab = False
		self.use_bubble = True

	def insert_text(self, substring, *args):
		if self.max_length and (len(self.text) == self.max_length):
			return
		super(CustomTextInput, self).insert_text(substring, *args)

	def validate(self, instance):
		if not instance.text:
			instance.background_color = [1, 0, 0, 1]