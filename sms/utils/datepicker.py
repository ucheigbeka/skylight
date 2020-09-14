import os
import calendar
from datetime import date

from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty, StringProperty

Builder.load_string('''
#: import os os
#: import NoTransition kivy.uix.screenmanager.NoTransition

<ImageButton@ButtonBehavior+Image>

<DatePickerBase>:
    canvas.before:
        Color:
            rgb: 0, 0, .2
        Rectangle:
            pos: self.pos
            size: self.size
    box: box
    manager: manager
    grid_manager: grid_manager
    year_txt: lbl.text
    orientation: 'vertical'
    CustomTextInput:
        id: lbl
        text: root.year_txt
        multiline: False
        size_hint: (None, None)
        size: (45, 30)
        pos_hint: {'center_x': .5}
        on_focus: if not args[1]: root.generate_days()
        on_text_validate: root.generate_days()
    BoxLayout:
        size_hint_y: .2
        ImageButton:
            source: os.path.join(root.base_dir, 'icons', 'icons8-back-64.png')
            on_release:
                manager.transition.direction = 'left'
                manager.current = manager.previous()
                root.generate_days()
        ScreenManager:
            id: manager
        ImageButton:
            source: os.path.join(root.base_dir, 'icons', 'icons8-next-page-64.png')
            on_release:
                manager.transition.direction = 'right'
                manager.current = manager.next()
                root.generate_days()
    BoxLayout:
        id: box
        size_hint_y: .2
    ScreenManager:
        id: grid_manager
        transition: NoTransition()
''')


class CustomTextInput(TextInput):
    def insert_text(self, substring, *args):
        if len(self.text) > 4:
            return
        super(CustomTextInput, self).insert_text(substring, *args)


weekdays = {'Mon': 0, 'Tue': 1, 'Wed': 2,
            'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
months = ['January', ' February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']


class DatePickerBase(BoxLayout):
    box = ObjectProperty()
    year_txt = StringProperty()
    manager = ObjectProperty()
    grid_manager = ObjectProperty()
    base_dir = os.path.dirname(__file__)

    def __init__(self, dropdown=None, **kwargs):
        super(DatePickerBase, self).__init__(**kwargs)
        self.disabled_color = (.1, .2, .3, 1)
        self.normal_color = (.5, .5, .5, 1)
        self.dropdown = dropdown if dropdown else DropDown()

        today = date.today()
        self.year_txt = str(today.year)

        for month in months:
            scr = Screen(name=month)
            scr.add_widget(Label(text=month))
            self.manager.add_widget(scr)
        self.manager.current = str(months[today.month - 1])

        # populate weekday labels
        [self.box.add_widget(Label(text=txt)) for txt in weekdays.keys()]

        # grid definition for 4 weeks
        self.grid_1 = GridLayout(cols=7)
        for i in range(7 * 4):
            btn = Button()
            btn.background_color = self.normal_color
            btn.bind(on_press=self.get_date)
            self.grid_1.add_widget(btn)
        scr_1 = Screen(name='Grid 1')
        scr_1.add_widget(self.grid_1)
        self.grid_manager.add_widget(scr_1)

        # grid definition for 5 weeks
        self.grid_2 = GridLayout(cols=7)
        for i in range(7 * 5):
            btn = Button()
            btn.background_color = self.normal_color
            btn.bind(on_press=self.get_date)
            self.grid_2.add_widget(btn)
        scr_1 = Screen(name='Grid 2')
        scr_1.add_widget(self.grid_2)
        self.grid_manager.add_widget(scr_1)

        # grid definition for 6 weeks
        self.grid_3 = GridLayout(cols=7)
        for i in range(7 * 6):
            btn = Button()
            btn.background_color = self.normal_color
            btn.bind(on_press=self.get_date)
            self.grid_3.add_widget(btn)
        scr_2 = Screen(name='Grid 3')
        scr_2.add_widget(self.grid_3)
        self.grid_manager.add_widget(scr_2)

        self.generate_days()

    def generate_days(self, *args):
        self.reset_bg_color()
        if not self.year_txt or int(self.year_txt) == 0: return
        monthCalendar = calendar.monthcalendar(
            int(self.year_txt), months.index(self.manager.current) + 1)

        if len(monthCalendar) == 4:
            count = len(self.grid_1.children) - 1
            for week in monthCalendar:
                for day in week:
                    if day:
                        self.grid_1.children[count].text = str(day)
                    else:
                        self.grid_1.children[count].text = ''
                        self.grid_1.children[count].background_color = self.disabled_color
                    count -= 1
            self.grid_manager.current = 'Grid 1'
        elif len(monthCalendar) == 5:
            count = len(self.grid_2.children) - 1
            for week in monthCalendar:
                for day in week:
                    if day:
                        self.grid_2.children[count].text = str(day)
                    else:
                        self.grid_2.children[count].text = ''
                        self.grid_2.children[count].background_color = self.disabled_color
                    count -= 1
            self.grid_manager.current = 'Grid 2'
        else:
            count = len(self.grid_3.children) - 1
            for week in monthCalendar:
                for day in week:
                    if day:
                        self.grid_3.children[count].text = str(day)
                    else:
                        self.grid_3.children[count].text = ''
                        self.grid_3.children[count].background_color = self.disabled_color
                    count -= 1
            self.grid_manager.current = 'Grid 3'

    def get_date(self, instance):
        if instance.text:
            selected_date = r'{day}/{month}/{year}'.format(day=instance.text,
                month=months.index(self.manager.current) + 1, year=self.year_txt)
            self.dropdown.select(selected_date)

    def reset_bg_color(self):
        for child in self.grid_manager.current_screen.children[0].children:
            child.background_color = self.normal_color


class DatePicker(Button):
    def __init__(self, **kwargs):
        super(DatePicker, self).__init__(**kwargs)

        self.dropdown = DropDown(auto_width=False, width=300)
        self.dropdown.bind(on_select=self.on_select)
        self.dropdown.add_widget(DatePickerBase(
            size_hint_y=None, height=200, dropdown=self.dropdown))

        self.add_widget(self.dropdown)
        self.dropdown.dismiss()

    def on_release(self, *args):
        self.dropdown.open(self)

    def on_select(self, instance, data):
        self.text = data


if __name__ == '__main__':
    from kivy.uix.floatlayout import FloatLayout
    layout = FloatLayout()
    layout.add_widget(DatePicker(pos_hint={
                      'center_x': .5, 'center_y': .5},
        size_hint=(None, None), size=(150, 40)))
    runTouchApp(layout)
