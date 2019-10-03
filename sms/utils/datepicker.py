import calendar
from datetime import date

from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ObjectProperty, StringProperty

Builder.load_string('''
<DatePicker>:
    canvas.before:
        Color:
            rgb: 1, 1, 0
        Rectangle:
            pos: self.pos
            size: self.size
    grid: grid
    manager: manager
    orientation: 'vertical'
    CustomTextInput:
        text: root.year_txt
        multiline: False
        size_hint: (None, None)
        size: (45, 30)
        pos_hint: {'center_x': .5}
    BoxLayout:
        size_hint_y: .2
        ImageButton:
            source: r'icons\icons8-back-64.png'
            on_release:
                manager.transition.direction = 'left'
                root.event()
                manager.current = manager.previous()
        ScreenManager:
            id: manager
        ImageButton:
            source: r'icons\icons8-next-page-64.png'
            on_release:
                manager.transition.direction = 'right'
                root.event()
                manager.current = manager.next()
    GridLayout:
        canvas.before:
            Color:
                rgb: 1, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        id: grid
        cols: 7
''')


class ImageButton(ButtonBehavior, Image):
    pass


class CustomTextInput(TextInput):
    def insert_text(self, substring, *args):
        if len(self.text) > 4:
            return
        super(CustomTextInput, self).insert_text(substring, *args)

weekdays = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
months = ['January', ' February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']
calendar.setfirstweekday(weekdays['Sun'])

class DatePicker(BoxLayout):
    grid = ObjectProperty()
    year_txt = StringProperty()
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        
        today = date.today()
        monthCalendar = calendar.monthcalendar(today.year, today.month)
        
        self.year_txt = str(today.year)
        self.month_txt = str(months[today.month - 1])

        for month in months:
            scr = Screen(name=month)
            scr.add_widget(Label(text=month))
            self.manager.add_widget(scr)
        self.manager.current = self.month_txt

        [self.grid.add_widget(Label(text=txt)) for txt in weekdays.keys()]

        for week in monthCalendar:
            [self.grid.add_widget(Button(text=str(day))) for day in week if day]

        self.event = Clock.create_trigger(self.generate_days)

    def generate_days(self, *args):
        self.grid.clear_widgets()

        monthCalendar = calendar.monthcalendar(int(self.year_txt), months.index(self.manager.current) + 1)
        [self.grid.add_widget(Label(text=txt)) for txt in weekdays.keys()]
        for week in monthCalendar:
            for day in week:
                if day:
                    self.grid.add_widget(Button(text=str(day)))
                else:
                    self.add_widget(Label())


if __name__ == '__main__':
    runTouchApp(DatePicker())
