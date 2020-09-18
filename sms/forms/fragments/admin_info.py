from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

Builder.load_string('''
<AdminInfo>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            padding: dp(50)
            spacing: dp(40)
            cols: 2
            size_hint: 1, .7
            row_default_height: dp(40)
            row_force_default: True
            CustomLabel:
                text: 'Vice Chancellor'
            CustomTextInput:
                font_size: sp(17)
                padding: dp(8)
                size_hint_x: .5
            CustomLabel:
                text: 'Chairman, Sub-Committee BCS'
            CustomTextInput:
                font_size: sp(17)
                padding: dp(8)
                size_hint_x: .5
            CustomLabel:
                text: 'Dean'
            CustomTextInput:
                font_size: sp(17)
                padding: dp(8)
                size_hint_x: .5
            CustomLabel:
                text: 'Faculty Exam Officer'
            CustomTextInput:
                font_size: sp(17)
                padding: dp(8)
                size_hint_x: .5
        FloatLayout:
            size_hint: 1, .3
            Button:
                text: 'Submit'
                size_hint: .3, .3
                pos_hint: {'x': .35, 'y': .7}
                font_size: 20
                background_color: 0, 1, 0, .5
''')


class AdminInfo(Screen):
    pass


if __name__ == '__main__':
    from kivy.app import runTouchApp

    Builder.load_string('''
<CustomTextInput@TextInput>:
    size_hint_x: None
    width: 300
    multiline: False
    write_tab: False
    use_bubble: True
    on_text_validate:
        if self.get_focus_next(): self.get_focus_next().focus = True

<CustomLabel@Label>:
    text_size: self.size
    size_hint_x: None
    width: 200
    halign: 'center'
        ''')

    runTouchApp(AdminInfo())
