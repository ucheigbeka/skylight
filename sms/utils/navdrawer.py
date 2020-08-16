from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import ObjectProperty, ListProperty, StringProperty

Builder.load_string('''
#:import NoTransition kivy.uix.screenmanager.NoTransition

<NavigationDrawer>:
    rv: rv
    sm: sm
    Splitter:
        sizable_from: 'right'
        rescale_with_parent: True
        min_size: dp(200)
        max_size: dp(300)
        RecycleView:
            id: rv
            viewclass: 'NavigationButton'
            data: root.toggle_btn_data
            RecycleBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(20)
                size_hint_y: None
                default_size: dp(100), dp(50)
                default_size_hint: 1, None
                height: self.minimum_height
    ScreenManager:
        id: sm
        nav_drawer: root
        transition: NoTransition()
''')


class NavigationButton(RecycleDataViewBehavior, ToggleButton):
    rv = ObjectProperty(None)
    screen_name = StringProperty('')

    def __init__(self, **kwargs):
        super(NavigationButton, self).__init__(**kwargs)
        self.group = 'nav_btn'

    def refresh_view_attrs(self, rv, index, data):
        super(NavigationButton, self).refresh_view_attrs(rv, index, data)
        self.rv = rv
        self.screen_name = data.get('text').lower()
        if index == 0:
            self.state = 'down'
        else:
            self.state = 'normal'

    def on_press(self):
        super(NavigationButton, self).on_press()
        self.state = 'down'
        self.switch_screen()

    def switch_screen(self):
        nav_drawer = self.rv.parent.parent
        nav_drawer.switch_screen(self.screen_name)


class NavigationDrawer(BoxLayout):
    rv = ObjectProperty(None)
    sm = ObjectProperty(None)

    toggle_btn_data = ListProperty()

    def add_screen(self, title, screen_obj):
        self.toggle_btn_data.append({'text': title})
        self.sm.add_widget(screen_obj(name=title.lower()))

    def switch_screen(self, screen_name):
        self.sm.current = screen_name


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.screenmanager import Screen

    class ChildWidget1(Screen):
        pass

    class ChildWidget2(Screen):
        pass

    class ChildWidget3(Screen):
        pass

    Builder.load_string('''
<ChildWidget1>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            padding: dp(50)
            spacing: 40
            cols: 2
            size_hint: 1, .7
            row_default_height: dp(40)
            row_force_default: True
            Label:
                text: 'New Vice Chancellor'
            TextInput:
                font_size: 17
                padding: 8
                multiline: False
                focus: True
            Label:
                text: 'New Dean'
            TextInput:
                multiline: False
                focus: True
                font_size: 17
                padding: 8
            Label:
                text: 'New HOD'
            TextInput:
                multiline: False
                focus: True
                font_size: 17
                padding: 8
            Label:
                text: 'New Exam Officer'
            TextInput:
                multiline: False
                focus: True
                font_size: 17
                padding: 8
        FloatLayout:
            size_hint: 1, .3
            Button:
                text: 'Submit'
                size_hint: None, None
                size_hint: .3, .3
                pos_hint: {'x': .35, 'y': .7}
                font_size: 20
                background_color: 0,1,0,.5
                
<ChildWidget2>
    Label:
        text: 'Project Skylight'

<ChildWidget3>
    Label:
        text: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'
        ''')

    nav_drawer = NavigationDrawer()
    nav_drawer.add_screen('New Admin Data', ChildWidget1)
    nav_drawer.add_screen('Main2', ChildWidget2)
    nav_drawer.add_screen('Main3', ChildWidget3)

    runTouchApp(nav_drawer)
