from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty

Builder.load_string('''
<PopupLabel>:
    text_size: self.size
    valign: 'middle'
    halign: 'center'

<DismissablePopupLabel>:
    orientation: 'vertical'
    PopupLabel:
        text: root.text
        markup: root.markup
    Button:
        size_hint_x: .3
        pos_hint: {'center_x': .5}
        text: 'Close'
        on_press: root.dismiss = True
''')


class PopupLabel(Label):
    pass


class DismissablePopupLabel(BoxLayout):
    text = StringProperty()
    markup = BooleanProperty(True)
    dismiss = BooleanProperty(False)


class ErrorPopup(Popup):
    def __init__(self, message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.title = kwargs.get('title', 'Error')
        if self.auto_dismiss:
            self.content = PopupLabel(text=message, markup=True)
        else:
            self.content = DismissablePopupLabel(text=message, markup=True)
            self.content.bind(dismiss=lambda ins, val: self.dismiss())
        self.size_hint = (.4, .2)

        self.open()


class SuccessPopup(Popup):
    def __init__(self, message, **kwargs):
        super(SuccessPopup, self).__init__(**kwargs)
        self.title = kwargs.get('title', 'Success')
        if self.auto_dismiss:
            self.content = PopupLabel(text=message, markup=True)
        else:
            self.content = DismissablePopupLabel(text=message, markup=True)
            self.content.bind(dismiss=lambda ins, val: self.dismiss())
        self.size_hint = (.4, .2)

        self.open()
