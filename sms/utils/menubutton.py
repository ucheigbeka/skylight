from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.properties import ListProperty

Builder.load_string('''
<ButtonBase>:
    font_size: sp(18)

<MenuButton>:
    background_color: (0, 0, 0, .2)
    size_hint_y: None
    height: dp(70)

<CustomActionButton>:
    canvas.before:
        Color:
            rgba: self.outline_color
        Line:
            rounded_rectangle: self.pos[0], self.pos[1], self.width, self.height, self.height / 8
            width: dp(2)
    color: self.outline_color
''')


class ButtonBase(Widget):
    def __init__(self, **kwargs):
        super(ButtonBase, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.highlight_btn)

    def highlight_btn(self, instance, value):
        pass


class CustomActionButton(ButtonBehavior, Label, ButtonBase):
    outline_color = ListProperty([0, 0.2, .98, .5])
    _outline_color = []

    def __init__(self, **kwargs):
        super(CustomActionButton, self).__init__(**kwargs)
        self._outline_color = self.outline_color.copy()

    def highlight_btn(self, instance, value):
        if self.disabled:
            return
        pos = self.to_widget(*value)
        if self.collide_point(*pos):
            self.outline_color = self.outline_color[:-1] + [1]
        else:
            self.outline_color = self._outline_color

    def on_touch_down(self, touch):
        if self.disabled:
            return False
        super(CustomActionButton, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self.outline_color = [1, 1, 0, 1]
            return True
        return False

    def on_touch_up(self, touch):
        if self.disabled:
            return False
        if self.collide_point(*touch.pos):
            self.outline_color = self._outline_color
            return True
        super(CustomActionButton, self).on_touch_up(touch)


class PositiveActionButton(CustomActionButton):
    outline_color = ListProperty([.1, .98, 0, .5])


class NegativeActionButton(CustomActionButton):
    outline_color = ListProperty([.98, 0, .1, .5])


class MenuButton(Button, ButtonBase):
    def highlight_btn(self, instance, value):
        pos = self.to_widget(*value)
        if self.collide_point(*pos):
            self.background_color = [.6, .8, 1, 1]
        else:
            self.background_color = [0, 0, 0, .2]


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.boxlayout import BoxLayout

    root = BoxLayout(orientation='vertical', spacing=10)
    root.add_widget(MenuButton(text='Hello World'))
    root.add_widget(MenuButton(text='Monty Python'))
    root.add_widget(PositiveActionButton(
        text='Monty Python', height=70, size_hint_y=None
    ))
    root.add_widget(NegativeActionButton(
        text='Monty Python', height=70, size_hint_y=None,
        disabled=True
    ))

    runTouchApp(root)
