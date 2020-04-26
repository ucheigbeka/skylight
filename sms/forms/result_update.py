'''
    data --> dict
        keys: no_of_pages --> int
              name --> str
              mat_no --> str
              mod --> int
              entry_session --> int
              results --> list
              credits --> list
              gpas --> list
              level_weightings --> list
              level_credits --> list
'''

from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanger import Screen
from kivy.properties import ListProperty

Builder.load_string('''

<ResultDataView@DataViewer>:
    cols: 5
    headers: ['COURSE CODE', 'COURSE TITLE', 'CREDIT', 'SCORE', 'GRADE']
    prop: {'disabled': True}
    offset_width = Window.width - 10
    widths: [offset_width * .2, offset_width * .5] + [offset_width * .1] * 3
    rv.do_scroll_y: False
    size_hint_y: None
    #content_layout: self.ids['content_layout']
    height: self.ids['content_layout'].height + dp(35)

<ResultViewBase>:
    do_scroll_x: False
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: first_sem_view.height + second_sem_view.height + 3 * dp(50)
        Label:
            text: 'xxxx/xxxx session'
            texture_size: self.text_size
            valign: 'middle'
            halign: 'left'
            size_hint_y: None
            height: dp(50)
        Label:
            text: 'First Semester'
            texture_size: self.text_size
            valign: 'middle'
            halign: 'left'
            size_hint_y: None
            height: dp(50)
        ResultDataView:
            id: first_sem_view
            _data: root.first_sem_data
        Label:
            text: 'Second Semester'
            texture_size: self.text_size
            valign: 'middle'
            halign: 'left'
            size_hint_y: None
            height: dp(50)
        ResultDataView:
            id: second_sem_view
            _data: root.second_sem_data
        FloatLayout:
            GridLayout:
                cols: 2
                size_hint: None, None
                height: self.minimum_height
                pos_hint: {'right': 1}

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            cols: 2
            CustomLabel:
                text: 'Matno'
            TextInput:
                disabled: True
            CustomLabel:
                text: 'Name'
            TextInput:
                disabled: True
            CustomLabel:
                text: 'Mode of entry'
            TextInput:
                disabled: True
            CustomLabel:
                text: 'Session of entry'
            TextInput:
                disabled: True
        ResultViewBase:
            first_sem_data: []
            second_sem_data: []

<IntermidiateScreen>:
    ResultViewBase:
        first_sem_data: []
        second_sem_data: []

<LastScreen>
''')


class ResultViewBase(ScrollView):
    first_sem_data = ListProperty()
    second_sem_data = ListProperty()


class MainScreen(Screen):
    pass


class IntermidiateScreen(Screen):
    pass


class LastScreen(Screen):
    pass


def generate_result_update_preview(data):
    pass
