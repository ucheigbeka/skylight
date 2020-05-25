from kivy.lang import Builder
from kivy.uix.stacklayout import StackLayout
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior, CompoundSelectionBehavior
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window

from kivy.graphics import Color, Rectangle

Builder.load_string('''
<MenuItem>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, .8
        Rectangle:
            pos: self.pos
            size: self.size

<MenuButton>:
    text_size: self.size
    halign: 'left'
    valign: 'center'
    size_hint_y: None
    height: 25
    ''')


class Menu(FocusBehavior, CompoundSelectionBehavior, StackLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.size_hint_y = .1

    def keyboard_on_key_up(self, window, keycode):
        if super(Menu, self).keyboard_on_key_up(window, keycode):
            return True
        if super(Menu, self).select_with_key_up(window, keycode):
            return True
        return False

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(Menu, self).keyboard_on_key_down(
            window, keycode, text, modifiers)


class MenuButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.highlight_btn)

    def highlight_btn(self, instance, value):
        if self.collide_point(*value):
            with self.canvas.before:
                Color(rgba=[.5, .5, 1, .2])
                Rectangle(pos=self.pos, size=self.size)
        else:
            with self.canvas.before:
                Color(rgba=[0, 0, 0, 1])
                Rectangle(pos=self.pos, size=self.size)


class MenuItem(MenuButton):
    def __init__(self, **kwargs):
        super(MenuItem, self).__init__(**kwargs)
        self.size_hint_x = None
        self.width = 100
        self.dropdown = DropDown(auto_width=False, width=200)

    def add_widget(self, wid, *args):
        self.dropdown.add_widget(wid, *args)

    def on_release(self):
        self.dropdown.open(self)


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.floatlayout import FloatLayout

    def callback(*args):
        print('New button clicked')

    def callback_1(*args):
        print('Exit button clicked')

    layout = FloatLayout()
    menu = Menu(pos_hint={'top': 1})
    menu_item = MenuItem(text='File')
    btn = MenuButton(text='New', on_release=callback)
    btn1 = MenuButton(text='Exit', on_release=callback_1)

    menu_item.add_widget(btn)
    menu_item.add_widget(btn1)
    menu.add_widget(menu_item)
    layout.add_widget(menu)

    runTouchApp(layout)
