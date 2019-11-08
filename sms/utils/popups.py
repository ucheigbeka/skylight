from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup

Builder.load_string('''
<PopupLabel>:
    text_size: self.size
    valign: 'middle'
    halign: 'center'
''')


class PopupLabel(Label):
    def __init__(self, **kwargs):
        super(PopupLabel, self).__init__(**kwargs)


class ErrorPopup(Popup):
    def __init__(self, message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.title = kwargs.get('title', 'Error')
        self.content = PopupLabel(text=message, markup=True)
        self.size_hint = (.4, .2)

        self.open()


class SuccessPopup(Popup):
    def __init__(self, message, **kwargs):
        super(SuccessPopup, self).__init__(**kwargs)
        self.title = kwargs.get('title', 'Success')
        self.content = PopupLabel(text=message, markup=True)
        self.size_hint = (.4, .2)

        self.open()
