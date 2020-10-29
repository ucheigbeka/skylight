from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout


Builder.load_string('''
<RadioButton>:
    id: radiobtn
    orientation: 'horizontal'
    group: 'btn'
    size_hint: 1, None
    height: dp(40) 
    spacing: dp(20)
    padding: dp(20)
    state: 'down' if self.selected else 'normal'
    
    CheckBox:
        group: "checkbox"
        # use selected Attribute to judge checkbox Status of
        state: 'down' if self.parent.selected else 'normal'
        size_hint: None, None
        size: lab.height, lab.height
    Label:
        id: lab
        text: self.parent.text if self.parent.text else 'RadioButton'
        size_hint: None, None
        size: self.texture_size
''')


class RadioButton(ToggleButtonBehavior, BoxLayout):
    selected = BooleanProperty(False)
    text = StringProperty('')

    def on_state(self, widget, value):
        if value == 'down':
            self.selected = True
        else:
            self.selected = False

    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)
            self.selected = True


if __name__ == '__main__':
    from kivy.app import runTouchApp

    Builder.load_string('''
<ToomaxWindow>:
    orientation: 'vertical'
    spacing: 2
    RadioButton:
        # Set the first radio button to selected
        # selected: True
        text: 'one'
        on_press: root.pp()
    RadioButton:
        text: 'ter'
        on_press: root.pq()
''')

    class ToomaxWindow(BoxLayout):
        def pp(self):
            print('works')

        def pq(self):
            print('works too')

    runTouchApp(ToomaxWindow())
