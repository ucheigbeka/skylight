import os
import json
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from sms import urlTo
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup, SuccessPopup
from sms.utils.dialog import OpenFileDialog

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'personalinfo.kv')
Builder.load_file(kv_path)


class PersonalInfo(Screen):
    form_root = form_root
    mat_no = StringProperty()

    def add(self, *args):
        data = dict()
        data['mat_no'] = self.ids.mat_no.text
        data['surname'] = self.ids.surname.text
        data['othernames'] = ' '.join([self.ids.fname.text, self.ids.mname.text])
        data['mode_of_entry'] = self.ids.mode_of_entry.values.index(self.ids.mode_of_entry.text) + 1
        data['session_admitted'] = int(self.ids.session_admit.text)
        data['current_level'] = int(self.ids.cur_level.text)
        data['sex'] = ['M', 'F'][self.ids.sex.text != 'Male']
        data['date_of_birth'] = self.ids.dob.text
        data['state_of_origin'] = self.ids.state_of_origin.text
        data['lga'] = self.ids.lga_of_origin.text
        data['phone_no'] = self.ids.phone_no.text
        data['email_address'] = self.ids.email.text
        data['sponsor_phone_no'] = self.ids.s_phone_no.text
        data['sponsor_email_address'] = self.ids.s_email.text
        data['grad_stats'] = int(self.ids.grad.text == 'YES')

        url = urlTo('personal_info')
        AsyncRequest(url, method='POST', data=data, on_success=self.record_added, on_failure=self.show_add_error)

    def cancel(self, *args):
        pass

    def search(self, *args):
        url = urlTo('personal_info')
        param = {'mat_no': self.mat_no}
        AsyncRequest(url, on_success=self.populate_fields, on_failure=self.show_error, params=param)

    def populate_fields(self, resp):
        data = json.loads(resp.json())
        self.ids.surname.text = data['surname']
        if len(data['othernames'].split()) == 2:
            self.ids.fname.text, self.ids.mname.text = data['othernames'].split()
        else:
            self.ids.fname.text, self.ids.mname.text = str(data['othernames']), ''
        self.ids.mode_of_entry.text = self.ids.mode_of_entry.values[data['mode_of_entry'] - 1]
        self.ids.session_admit.text = str(data['session_admitted'])
        self.ids.cur_level.text = str(data['current_level'])
        self.ids.sex.text = self.ids.sex.values[data['sex'] != 'M']
        self.ids.dob.text = str(data['date_of_birth'])
        self.ids.state_of_origin.text = str(data['state_of_origin'])
        self.ids.lga_of_origin.text = str(data['lga'])
        self.ids.phone_no.text = str(data['phone_no'])
        self.ids.email.text = str(data['email_address'])
        self.ids.s_phone_no.text = str(data['sponsor_phone_no'])
        self.ids.s_email.text = str(data['sponsor_email_address'])
        self.ids.grad.text = self.ids.grad.values[not bool(data['grad_stats'])]

    def show_error(self, resp):
        ErrorPopup('Record not found')

    def show_add_error(self, resp):
        ErrorPopup('Record could not be added')

    def record_added(self, resp):
        SuccessPopup('Record added')
        self.clear_fields()

    def load_image(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.is_double_tap:
            filter_dict = {'All Picture Files': ['*.png', '*.jpeg', '*.jpg', '*.jpe', '*.jfif'], 'PNG (*.png)': ['*.png'], 
                            'JPEG (*.jpeg; *.jpg; *.jpe; *.jfif)': ['*.jpeg', '*.jpg', '*.jpe', '*.jfif'], 
                            'All Files': ['*']}
            dialog = OpenFileDialog(filter_dict=filter_dict)
            dialog.bind(on_dismiss=self.render_image)
            dialog.open()

    def render_image(self, instance):
        if instance.selected_path:
            self.ids['passport'].source = instance.selected_path
            self.ids['passport'].allow_stretch = True
            self.ids['passport'].keep_ratio = False

    def clear_fields(self):
        fields = list(self.ids.keys())
        fields.remove('grid')
        fields.remove('passport')
        for field in fields:
            self.ids[field].text = ''
        self.ids.mat_no.text = 'ENG'
        self.ids.passport.source = ''

    def on_leave(self):
        self.clear_fields()


if __name__ == '__main__':
    from kivy.app import runTouchApp

    runTouchApp(PersonalInfo())
