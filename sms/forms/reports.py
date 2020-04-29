import os
from threading import Thread
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from sms.forms.template import FormTemplate
from sms.forms.result_update import generate_result_update_preview
from sms.utils.tabbedview import CustomTabbedPanelHeader

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'reports.kv')
Builder.load_file(kv_path)


class Reports(FormTemplate):
    tabbed_panel = ObjectProperty(None)

    def generate_report(self, data, tab_title, report_type):
        if report_type == 'result_update':
            screens = generate_result_update_preview(data)
        Thread(target=self.add_screens, args=(tab_title, screens)).start()

    def add_screens(self, tab_title, screens):
        tab_header = CustomTabbedPanelHeader(text=tab_title)
        for screen in screens:
            tab_header.add_screen(screen)
        self.tabbed_panel.add_widget(tab_header)
