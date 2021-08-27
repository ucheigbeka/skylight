from kivy.lang import Builder
from kivy.properties import BooleanProperty

from sms import get_kv_path, urlTo, AsyncRequest, root
from sms.forms.template import FormTemplate
from sms.scripts.migrate_session import SessionMigrationPopup
from sms.utils.menubar import color_disabled_switch
from sms.utils.popups import ErrorPopup, YesNoPopup

kv_path = get_kv_path('admin')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class Administrator(FormTemplate):
    title = 'Administrator'
    switch_active = BooleanProperty(False)
    
    def migrate_session(self):
        YesNoPopup('Are you sure you want to start a new academic session?', on_yes=self.open_session_migarion_popup)

    def open_session_migarion_popup(self):
        SessionMigrationPopup().open()

    def on_enter(self, *args):
        # give the disabled switch the colors of an enabled one
        switch = self.ids.get('result_switch', None)
        if switch:
            color_disabled_switch(switch)
            self.set_res_switch_state(state=root.menu_bar.action_view.ids['result_switch'].active)
        super(Administrator, self).on_enter(*args)

    def set_res_switch_state(self, resp=None, state=None):
        self.switch_active = bool(resp.json()) if resp else state
        switch = self.ids['result_switch']
        switch.active = self.switch_active
        if resp:
            root.set_res_switch_state(resp)  # sets the menu_bar switch state

    def set_results_edit(self):
        switch = self.ids['result_switch']
        url = urlTo('results_edit')
        data = {'state': int(not switch.active)}
        AsyncRequest(url, method='POST', data=data, on_success=self.set_res_switch_state)

    def show_error(self, resp):
        try:
            msg = resp.json()
        except:
            msg = 'Something went wrong'
        msg = msg['details'] if 'details' in msg else msg
        ErrorPopup(msg)
