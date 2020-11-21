from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty

from sms import get_addr, set_addr
from sms.utils.popups import PopupBase

Builder.load_string('''
<ServerConfigContent>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    GridLayout:
        cols: 2
        size_hint_y: .7
        valign: 'center'
        spacing: dp(20), dp(10)
        row_default_height: dp(30)
        row_force_default: True
        CustomLabel:
            text: 'Protocol'
            halign: 'left'
            size_hint_x: .3
        CustomSpinner:
            id: protocol
            size_hint_x: .6
            values: ['http', 'https']
        CustomLabel:
            text: 'Host'
            halign: 'left'
            size_hint_x: .3
        CustomTextInput:
            id: host
            size_hint_x: .6
        CustomLabel:
            text: 'Port'
            halign: 'left'
            size_hint_x: .3
        CustomTextInput:
            id: port
            input_filter: 'int'
            max_length: 5
            size_hint_x: .6
    BoxLayout:
        size_hint_y: .3
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
        protocol, host, port = get_addr()
        self.ids['protocol'].text = protocol
        self.ids['host'].text = host
        self.ids['port'].text = str(port)

    def save(self):
        protocol = self.ids['protocol'].text
        host = self.ids['host'].text
        port = int(self.ids['port'].text)
        set_addr((protocol, host, port))
        self.dismiss = True


class ServerConfigPopup(PopupBase):
    def __init__(self, **kwargs):
        self.content = ServerConfigContent()
        self.content.bind(dismiss=lambda ins, val: self.dismiss())
        super(ServerConfigPopup, self).__init__(title='Server Config', auto_dismiss=False, **kwargs)
        self.size_hint = (.3, .35)

    def on_open(self):
        self.content.populate_fields()
