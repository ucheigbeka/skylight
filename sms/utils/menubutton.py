from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.button import Button

Builder.load_string('''
<MenuButton>:
    size_hint_y: .1
    font_size: 18
    background_color: (0, 0, 0, .2)
''')


class MenuButton(Button):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.highlight_btn)

    def highlight_btn(self, instance, value):
        pos = self.to_widget(*value)
        if self.collide_point(*pos):
            self.background_color = [.6, .8, 1, 1]
        else:
            self.background_color = [0, 0, 0, .2]


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.boxlayout import BoxLayout

    root = BoxLayout(orientation='vertical')
    root.add_widget(MenuButton(text='Hello World'))
    root.add_widget(MenuButton(text='Monty Python'))

    runTouchApp(root)
