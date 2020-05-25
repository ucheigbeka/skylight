import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from sms.forms.template import FormTemplate
from sms.utils.tabbedview import CustomTabbedPanelHeader

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'reports.kv')
Builder.load_file(kv_path)


class Reports(FormTemplate):
    tabbed_panel = ObjectProperty(None)

    def on_enter(self, *args):
        tabs = self.tabbed_panel.tab_list
        self.tabbed_panel.switch_to(tabs[0])

    def generate_report(self, screens, tab_title):
        self.add_screens(tab_title, screens)

    def add_screens(self, tab_title, screens):
        tab_header = CustomTabbedPanelHeader(text=tab_title)
        for screen in screens:
            tab_header.add_screen(screen)
        self.tabbed_panel.add_widget(tab_header)
