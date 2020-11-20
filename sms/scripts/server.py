from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty

from sms import get_addr, set_addr
from sms.utils.popups import PopupBase

Builder.load_string('''
<ServerConfigContent>:
    orientation: 'vertical'
    GridLayout:
        cols: 2
        spacing: dp(10), dp(5)
        padding: dp(10)
        row_default_height: dp(30)
        row_force_default: True
        CustomLabel:
            text: 'Host'
            size_hint_x: .4
        CustomTextInput:
            id: host
            size_hint_x: .5
        CustomLabel:
            text: 'Port'
            size_hint_x: .4
        CustomTextInput:
            id: port
            input_filter: 'int'
            max_length: 4
            size_hint_x: .5
    BoxLayout:
        size_hint_y: .4
        spacing: dp(10)
        Button:
            text: 'Save'
            on_press: root.save()
        Button:
            text: 'Close'
            on_press: root.dismiss = True
''')


class ServerConfigContent(BoxLayout):
    dismiss = BooleanProperty(False)

    def populate_fields(self):
        host, port = get_addr()
        self.ids['host'].text = host
        self.ids['port'].text = str(port)

    def save(self):
        host = self.ids['host'].text
        port = int(self.ids['port'].text)
        addr = (host, port)
        set_addr(addr)
        self.dismiss = True


class ServerConfigPopup(PopupBase):
    def __init__(self, **kwargs):
        self.content = ServerConfigContent()
        self.content.bind(dismiss=lambda ins, val: self.dismiss())
        super(ServerConfigPopup, self).__init__(title='Server Config', auto_dismiss=False, **kwargs)
        self.size_hint = (.3, .3)

    def on_open(self):
        self.content.populate_fields()
