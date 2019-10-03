from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_string('''
<CustomLabel>:
	text_size: self.size
	size_hint_x: None
	width: 200
	halign: 'center'
''')


class CustomLabel(Label):
	pass
