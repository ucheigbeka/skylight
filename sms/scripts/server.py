from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty

from sms import get_addr, set_addr
from sms.config import Config
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
            valign: 'center'
            size_hint_x: .3
        CustomSpinner:
            id: protocol
            size_hint_x: .6
            valign: 'center'
            values: ['http', 'https']
        CustomLabel:
            text: 'Host'
            halign: 'left'
            valign: 'center'
            size_hint_x: .3
        CustomTextInput:
            id: host
            size_hint_x: .6
            valign: 'center'
        CustomLabel:
            text: 'Port'
            halign: 'left'
            valign: 'center'
            size_hint_x: .3
        GridLayout:
            cols: 2
            size_hint_x: .7
            spacing: dp(15), dp(0)
            row_default_height: dp(30)
            row_force_default: True
            CustomSpinner:
                id: profile
                size_hint_x: .7
                valign: 'center'
                on_text: root.update_port()
            CustomTextInput:
                id: port
                input_filter: 'int'
                valign: 'center'
                max_length: 5
                size_hint_x: .3
    BoxLayout:
        size_hint_y: .2
        spacing: dp(10)
        Button:
            text: 'Save'
            on_press: root.save()
        Button:
            text: 'Default'
            on_press: root.restore_default()
        Button:
            text: 'Close'
            on_press: root.dismiss = True
''')


class ServerConfigContent(BoxLayout):
    dismiss = BooleanProperty(False)
    profiles = {
        'Mechanical': 1807,
        'Mechatronics': 1808,
        'Met and Mat': 1809,
        'Marine': 1810
    }

    def populate_fields(self):
        protocol, host, port = get_addr()
        self.ids['protocol'].text = protocol
        self.ids['host'].text = host
        self.ids['profile'].values = self.profiles.keys()
        self.ids['port'].text = str(port)
        dept = [k for k, v in self.profiles.items() if v == port]
        self.ids['profile'].text = dept[0] if dept else ''

    def update_port(self):
        profile = self.ids['profile'].text
        self.ids['port'].text = str(self.profiles.get(profile, 1807))

    def save(self):
        protocol = self.ids['protocol'].text
        host = self.ids['host'].text
        port = int(self.ids['port'].text)
        set_addr((protocol, host, port))
        self.dismiss = True

    def restore_default(self):
        Config.restore_default('backend')
        self.populate_fields()


class ServerConfigPopup(PopupBase):
    def __init__(self, **kwargs):
        self.content = ServerConfigContent()
        self.content.bind(dismiss=lambda ins, val: self.dismiss())
        super(ServerConfigPopup, self).__init__(title='Server Config', auto_dismiss=False, **kwargs)
        self.size_hint = (.3, .4)

    def on_open(self):
        self.content.populate_fields()
