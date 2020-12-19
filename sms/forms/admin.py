from kivy.lang import Builder

from sms import get_kv_path, urlTo, AsyncRequest, root
from sms.forms.template import FormTemplate
from sms.utils.popups import ErrorPopup

kv_path = get_kv_path('admin')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class Administrator(FormTemplate):
    title = 'Administrator'
    switch_active = False

    def on_enter(self, *args):
        self.get_results_edit()
        super(Administrator, self).on_enter(*args)

    def get_results_edit(self):
        url = urlTo('results_edit')
        AsyncRequest(url, on_success=self.set_res_switch_state)

    def set_res_switch_state(self, resp):
        self.switch_active = bool(resp.json())
        switch = self.ids['result_switch']
        switch.active = self.switch_active
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
