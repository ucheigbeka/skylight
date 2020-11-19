from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from sms import urlTo, AsyncRequest
from sms.utils.popups import PopupBase, SuccessPopup, ErrorPopup

Builder.load_string('''
<FeedbackPopupContent>:
    BoxLayout:
        orientation: "vertical"
        spacing: dp(30)
        padding: dp(20)

        CustomTextInput:
            id: message
            hint_text: "Type your feedback or error report"
            size_hint_x: 1
            focus: True
            on_text_validate: root.send_feedback()
        MenuButton:
            text: "Send Feedback"
            size_hint_y: .8
            on_press: root.send_feedback()
''')


class FeedbackPopup(PopupBase):
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', 'Feedback')
        self.content = FeedbackPopupContent()
        self.content.dismiss = self.dismiss
        self.content.username = kwargs.pop('username', None)
        self.size_hint = (.4, .4)
        super(FeedbackPopup, self).__init__(**kwargs)


class FeedbackPopupContent(BoxLayout):
    username = StringProperty()
    dismiss = None

    def send_feedback(self):
        from main import prev_log, fd
        url = urlTo('feedback')
        data = {
            'username': self.username,
            'message': self.ids['message'].text,
            'error_log': 'Previous App Session\n' + '='*20 + '\n' + prev_log +
                         '\n\nCurrent App Session\n' + '='*19 + '\n' + fd.read()
        }
        AsyncRequest(url, method='POST', data=data, on_success=self.show_message, on_failure=self.show_message)

    def show_message(self, resp):
        if resp.status_code == 200:
            SuccessPopup('Feedback sent')
        else:
            ErrorPopup('Something went wrong')
        self.dismiss()
