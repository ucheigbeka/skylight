from kivy.lang import Builder
from kivy.uix.label import Label

Builder.load_string('''
<CustomLabel>:
    text_size: self.size
    size_hint_x: None
    width: 200
    halign: 'center'

<HeaderLabel@Label>:
    canvas.before:
        Color:
            rgba: 0, .4, .4, 1
        Rectangle:
            pos: self.pos
            size: self.size

    text_size: self.size
    halign: 'center'
    valign: 'middle'
''')


class CustomLabel(Label):
    pass
