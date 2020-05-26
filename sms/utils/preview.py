import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

Builder.load_string('''
<Preview>:
    FloatLayout:
        AsyncImage:
            a: bool(print(os.path.join(root.base_dir, 'icons', 'print.png')))
            source: os.path.join(root.base_dir, 'icons', 'print.png')
            size_hint: None, None
            pos_hint: {'right': 1, 'top': 1}
            width: 50
            height: int(self.width / self.image_ratio)
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: int(root.width * 1 / 2)
            pos_hint: {'center_x': .5}
            AsyncImage:
                source: root.source
                size_hint_y: None
                height: int(self.width / self.image_ratio)
            FloatLayout:
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
''')


class Preview(Screen):
    source = StringProperty()
    base_dir = StringProperty(os.path.dirname(__file__))
