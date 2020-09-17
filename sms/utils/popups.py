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
    markup: True

<DismissablePopupLabel>:
    orientation: 'vertical'
    PopupLabel:
        text: root.text
        markup: True
    Button:
        size_hint_x: .3
        pos_hint: {'center_x': .5}
        text: 'Close'
        on_press: root.dismiss = True

<YesNoPopupContent>:
    orientation: 'vertical'
    PopupLabel:
        text: root.text
        markup: True
    BoxLayout:
        size_hint_x: .3
        Button:
            text: 'Yes'
            on_press: root.yes()
        Button:
            text: 'No'
            on_press: root.no()
''')


class PopupLabel(Label):
    pass


class DismissablePopupLabel(BoxLayout):
    text = StringProperty()
    dismiss = BooleanProperty(False)


class YesNoPopupContent(BoxLayout):
    text = StringProperty()
    yes_func = None
    no_func = None
    end_func = None

    def yes(self):
        if self.yes_func:
            self.yes_func()
        self.end_func()

    def no(self):
        if self.no_func:
            self.no_func()
        self.end_func()

    def set_callbacks(self, yes, no, end_func):
        self.yes_func = yes
        self.no_func = no
        self.end_func = end_func


class PopupBase(Popup):
    def __init__(self, message=None, **kwargs):
        super(PopupBase, self).__init__(**kwargs)
        if not self.content:
            if self.auto_dismiss:
                self.content = PopupLabel(text=message)
            else:
                self.content = DismissablePopupLabel(text=message)
                self.content.bind(dismiss=lambda ins, val: self.dismiss())
            self.size_hint = (.4, .2)

        self.open()


class ErrorPopup(PopupBase):
    def __init__(self, message, **kwargs):
        self.title = kwargs.get('title', 'Error')
        super(ErrorPopup, self).__init__(message, **kwargs)


class SuccessPopup(PopupBase):
    def __init__(self, message, **kwargs):
        self.title = kwargs.get('title', 'Success')
        super(SuccessPopup, self).__init__(message, **kwargs)


class YesNoPopup(PopupBase):
    def __init__(self, message, on_yes=None, on_no=None, **kwargs):
        self.title = kwargs.get('title', 'Info')
        self.content = YesNoPopupContent(text=message)
        self.content.set_callbacks(on_yes, on_no, self.dismiss)
        self.auto_dismiss = False
        super(YesNoPopup, self).__init__(**kwargs)
