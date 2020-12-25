import os
import subprocess
import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty

from sms.utils.popups import ErrorPopup

Builder.load_string('''
<Preview>:
    box: box
    sv: sv
    ScrollView:
        id: sv
        effect_cls: 'ScrollEffect'
        BoxLayout:
            id: box
            orientation: 'vertical'
            AsyncImage:
                pos_hint: {'center_x': .5}
                keep_ratio: False
                allow_stretch: True
                size_hint_x: (box.height * self.image_ratio) / box.width
                source: root.source
    ImageButton:
        source: root.print_icon_dir
        size_hint: None, None
        pos_hint: {'right': 1, 'top': 1}
        width: 50
        height: int(self.width / self.image_ratio)
        on_press: root.print_pdf()
''')

base_dir = os.path.dirname(__file__)


class Preview(Screen):
    box = ObjectProperty()
    sv = ObjectProperty()
    source = StringProperty()
    filepath = StringProperty()
    print_icon_dir = StringProperty(
        os.path.join(base_dir, 'icons', 'icons8-print-32.png'))
    cursor_change_event = None

    def __init__(self, **kwargs):
        super(Preview, self).__init__(**kwargs)
        self.num_zooms = 0
        reports_scr = App.get_running_app().root.sm.get_screen('reports')
        reports_scr.bind(on_enter=self.schedule_cursor_change)
        reports_scr.bind(on_leave=self.unschedule_cursor_change)

    def schedule_cursor_change(self, *args, **kwargs):
        self.cursor_change_event = Clock.schedule_interval(self.change_cursor, 1 / 6)

    def unschedule_cursor_change(self, *args, **kwargs):
        Clock.unschedule(self.cursor_change_event)
        Window.set_system_cursor('arrow')

    def change_cursor(self, dt):
        pos = self.to_widget(*Window.mouse_pos)
        if self.box.collide_point(*pos):
            Window.set_system_cursor('size_all')
        else:
            Window.set_system_cursor('arrow')

    def print_pdf(self):
        cwd = os.getcwd()
        os.chdir(os.path.expanduser('~'))
        if sys.platform == 'win32':
            try:
                os.startfile(self.filepath, 'print')
            except OSError:
                os.startfile(self.filepath)
        else:
            try:
                subprocess.run(['xdg-open', self.filepath])
            except:
                ErrorPopup(f'Error trying to print {self.filepath}\nOS currently not supported')
        os.chdir(cwd)

    def on_touch_down(self, touch):
        self.box.size_hint = (None, None)
        if self.box.collide_point(*touch.pos) and touch.is_double_tap and touch.button == 'left':
            if self.num_zooms > 3:
                return
            self.box.width *= 1.2
            self.box.height *= 1.2
            self.sv.scroll_x = (touch.pos[0] / Window.width)
            self.sv.scroll_y = (touch.pos[1] / Window.height)
            self.num_zooms += 1
            return True
        elif self.box.collide_point(*touch.pos) and touch.is_double_tap and touch.button == 'right':
            if not self.num_zooms:
                return
            self.box.width /= 1.2
            self.box.height /= 1.2
            self.sv.scroll_x = (touch.pos[0] / Window.width)
            self.sv.scroll_y = (touch.pos[1] / Window.height)
            self.num_zooms -= 1
            return True
        super(Preview, self).on_touch_down(touch)
