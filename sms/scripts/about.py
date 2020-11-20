from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty

from sms import get_username
from sms.scripts.feedback import FeedbackPopup
from sms.utils.popups import PopupBase

Builder.load_string('''
#:import PopupLabel sms.utils.popups.PopupLabel

<AboutPopupContent>:
    orientation: 'vertical'
    PopupLabel:
        text: root.msg
    BoxLayout:
        size_hint_y: .5
        spacing: dp(10)
        Button:
            text: 'Send feedback'
            on_press: root.open_feedback()
        Button:
            text: 'Close'
            on_press: root.dismiss = True
''')


class AboutPopupContent(BoxLayout):
    msg = StringProperty()
    dismiss = BooleanProperty(False)

    def open_feedback(self):
        FeedbackPopup(username=get_username())
        self.dismiss = True


class AboutPopup(PopupBase):
    def __init__(self, **kwargs):
        msg = ''' Student Management System
        
        Feedback Icon made by Those Icons from www.flaticon.com
        '''
        self.content = AboutPopupContent(msg=msg)
        self.content.bind(dismiss=lambda ins, val: self.dismiss())
        self.size_hint = (.4, .27)
        super(AboutPopup, self).__init__(title='Project Skylight', auto_dismiss=False, **kwargs)


def about():
    AboutPopup()
