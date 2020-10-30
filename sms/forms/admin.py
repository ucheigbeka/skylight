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

    def set_results_edit(self):
        switch = self.ids['result_switch']
        url = urlTo('results_edit')
        data = {'state': switch.active}
        AsyncRequest(url, method='POST', data=data, on_success=self.sing_for_me, on_failure=self.show_error)

    def sing_for_me(self, resp):
        state = resp.json()
        msg = 'Result Edit {}'.format('opened' if state else 'closed')
        SuccessPopup(message=msg)

    def show_error(self, resp):
        try:
            msg = resp.json()
        except:
            msg = 'Something went wrong'
        msg = msg['details'] if 'details' in msg else msg
        ErrorPopup(msg)
