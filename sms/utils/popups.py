import os
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty

Builder.load_string('''
#:import os os

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
        size_hint_y: .2
        spacing: dp(10)
        Button:
            text: 'Yes'
            on_press: root.yes()
        Button:
            text: 'No'
            on_press: root.no()

<LoadPopup>:
    BoxLayout:
        padding: 0, dp(10)
        AsyncImage:
            source: os.path.join(root.base_dir, 'icons', 'progress-80.gif')
            anim_delay: 1 / 24
            size_hiny: None, None
            size: self.texture_size
        PopupLabel:
            text: root.text
            text_size: self.size
            halign: 'left'
            markup: True
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
        self.end()

    def no(self):
        if self.no_func:
            self.no_func()
        self.end()

    def end(self):
        if self.end_func:
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
        self.size_hint = (.3, .4)
        super(YesNoPopup, self).__init__(**kwargs)


class LoadPopup(ModalView):
    base_dir = os.path.dirname(__file__)
    text = StringProperty()

    def __init__(self, **kwargs):
        super(LoadPopup, self).__init__(**kwargs)
        self.size_hint = (.25, .15)
        self.auto_dismiss = False

    def open(self, *args, text=None, **kwargs):
        if not text:
            text = 'Loading...'
        self.text = text
        super(LoadPopup, self).open(*args, **kwargs)


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.button import Button
    from sms.forms.signin import SigninPopup


    def yes():
        print('Yes')

    def no():
        print('No')

    def callback(ins):
        # YesNoPopup('This is a test', on_yes=yes, on_no=no)
        # LoadPopup().open()
        SigninPopup(signin_window_object=None)

    btn = Button(text='Test', on_press=callback)
    runTouchApp(btn)
