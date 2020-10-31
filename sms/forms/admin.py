from kivy.lang import Builder

from sms import get_kv_path, urlTo, AsyncRequest
from sms.forms.template import FormTemplate
from sms.utils.popups import ErrorPopup, SuccessPopup

kv_path = get_kv_path('admin')
Builder.load_file(kv_path)


def unload():
    Builder.unload_file(kv_path)


class Administrator(FormTemplate):
    title = 'Administrator'

    def on_enter(self, *args):
        self.get_results_edit()
        super(Administrator, self).on_enter(*args)

    def get_results_edit(self):
        url = urlTo('results_edit')
        AsyncRequest(url, on_success=self.set_res_switch_state)

    def set_res_switch_state(self, resp):
        state = resp.json()
        switch = self.ids['result_switch']
        switch.active = bool(state)

    def set_results_edit(self):
        switch = self.ids['result_switch']
        url = urlTo('results_edit')
        data = {'state': int(switch.active)}
        AsyncRequest(url, method='POST', data=data)

    # def success_popup(self, resp):
    #     state = resp.json()
    #     msg = 'Result Edit {}'.format('opened' if state else 'closed')
    #     SuccessPopup(message=msg)

    def show_error(self, resp):
        try:
            msg = resp.json()
        except:
            msg = 'Something went wrong'
        msg = msg['details'] if 'details' in msg else msg
        ErrorPopup(msg)
