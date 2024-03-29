import os
import json
from kivy.lang import Builder
from kivy.properties import StringProperty

from sms import urlTo, get_assigned_level, root, get_current_session
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup, SuccessPopup, YesNoPopup
from sms.utils.dialog import OpenFileDialog

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'personalinfo.kv')
Builder.load_file(kv_path)

MODES_OF_ENTRY = ['PUTME', 'DE (200)', 'DE (300)']
EXTRAS = {}


def unload():
    Builder.unload_file(kv_path)


def insert_extra(extra):
    EXTRAS.update(extra)


class PersonalInfo(FormTemplate):
    title = 'Personal Information'
    profile_icon = StringProperty(os.path.join(
        form_root, 'resc', 'icons', 'icons8-edit-profile-480.png'))

    def setup(self):
        self.ids.mat_no.text = 'ENG'
        self.ids.session_admit.text = str(get_current_session())
        self.ids.passport.source = self.profile_icon
        self.ids['dob'].text = ''
        self.ids['btn_positive'].text = 'Add'
        if not self.manager.is_admin:
            assigned_level = get_assigned_level()
            self.ids['level'].text = str(assigned_level)
            if assigned_level in range(100, 400):
                self.ids['mode_of_entry'].values = [MODES_OF_ENTRY[(assigned_level // 100) - 1]]
            else:
                self.ids['mode_of_entry'].disabled = True
                self.ids['btn_positive'].disabled = True
        elif self.manager.is_admin == 2:
            self.ids['level'].values = [str(i) for i in range(100, 400, 100)]
            self.ids['mode_of_entry'].values = MODES_OF_ENTRY
        else:
            self.ids['level'].values = [str(i) for i in range(100, 1000, 100)]
            self.ids['mode_of_entry'].values = MODES_OF_ENTRY

    def on_enter(self, *args):
        super(PersonalInfo, self).on_enter(*args)
        if EXTRAS:
            self.ids['mat_no'].text = EXTRAS.get('mat_no')
            self.search()

    def search(self, *args):
        url = urlTo('personal_info')
        param = {'mat_no': self.ids.mat_no.text}
        AsyncRequest(url, on_success=self.populate_fields, on_failure=self.show_error, params=param)

    def populate_fields(self, resp):
        data = json.loads(resp.json())
        self.ids.surname.text = data['surname']
        self.ids.fname.text, _, self.ids.mname.text = data['othernames'].partition(' ')
        self.ids.mode_of_entry.text = MODES_OF_ENTRY[data['mode_of_entry'] - 1]
        self.ids.session_admit.text = str(data['session_admitted'])
        self.ids.level.text = str(data['level'])
        self.ids.transfer.text = 'Yes' if data['transfer'] else 'No'
        self.ids.sex.text = self.ids.sex.values[data['sex'] != 'M']
        self.ids.dob.text = str(data['date_of_birth']) if data['date_of_birth'] else ''
        self.ids.state_of_origin.text = str(data['state_of_origin']) if data['state_of_origin'] else ''
        self.ids.lga_of_origin.text = str(data['lga']) if data['lga'] else ''
        self.ids.phone_no.text = str(data['phone_no']) if data['phone_no'] else ''
        self.ids.email.text = str(data['email_address']) if data['email_address'] else ''
        self.ids.s_phone_no.text = str(data['sponsor_phone_no']) if data['sponsor_phone_no'] else ''
        self.ids.s_email.text = str(data['sponsor_email_address']) if data['sponsor_email_address'] else ''
        self.ids.grad.text = self.ids.grad.values[not bool(data['grad_status'])]
        self.ids.session_grad.text = str(data['session_grad']) if data['session_grad'] else ''

        option = (data["option"] or '').partition(',')
        self.ids.option_1.text = option[0].partition(' ')[2]
        self.ids.option_2.text = option[2].partition(' ')[2]

        self.ids['btn_positive'].text = 'Update'
        self.ids['btn_positive'].disabled = False if data['level'] == get_assigned_level() or root.sm.is_admin else True
        self.ids['delete'].disabled = False if data['level'] == get_assigned_level() or root.sm.is_admin else True

    def add_update(self):
        method = ['POST', 'PATCH'][self.ids['btn_positive'].text == 'Update']
        compulsory_fields = ("mat_no", "surname", "fname", "mode_of_entry", "session_admit", "level", "sex", "phone_no",
                             "email")
        if not self.validate_inputs(include=compulsory_fields):
            self.show_input_error()
            return
        data = dict()
        data['mat_no'] = self.ids.mat_no.text
        data['surname'] = self.ids.surname.text.upper()
        data['othernames'] = ' '.join([self.ids.fname.text.capitalize(), self.ids.mname.text.capitalize()]).strip()
        data['mode_of_entry'] = MODES_OF_ENTRY.index(self.ids.mode_of_entry.text) + 1
        data['session_admitted'] = int(self.ids.session_admit.text)
        data['level'] = int(self.ids.level.text)
        data['sex'] = ['M', 'F'][self.ids.sex.text != 'Male']
        data['phone_no'] = self.ids.phone_no.text
        data['email_address'] = self.ids.email.text

        opt = [self.ids.option_1.text.strip(), self.ids.option_2.text.strip()]
        if any(opt):
            data['option'] = f"1 {opt[0]},2 {opt[1]}"

        # not required
        optionals = {
            'lga': self.ids.lga_of_origin.text,
            'date_of_birth': self.ids.dob.text,
            'state_of_origin': self.ids.state_of_origin.text,
            'sponsor_phone_no': self.ids.s_phone_no.text,
            'sponsor_email_address': self.ids.s_email.text,
            'transfer': int(self.ids.transfer.text == 'Yes'),
            'session_grad': int(self.ids.session_grad.text or 0),
            'grad_status': int(self.ids.grad.text == 'YES')
        }
        [data.update({k:v}) for (k,v) in optionals.items() if v is not None]
        url = urlTo('personal_info')
        AsyncRequest(url, method=method, params=data, on_success=self.record_added, on_failure=self.show_add_error)

    def delete(self):
        YesNoPopup(message="Do you want to delete this student's record?", on_yes=self._delete)

    def _delete(self):
        params = {"mat_no": self.ids.mat_no.text}
        url = urlTo('personal_info')
        AsyncRequest(url, params=params, method='DELETE', on_success=self.record_deleted, on_failure=self.show_error)

    def show_error(self, resp):
        try:
            error = resp.json()
            if isinstance(error, dict):
                error = error.get("detail", "")
        except Exception as e:
            error = ""
        ErrorPopup(error or "Record not found")

    def show_add_error(self, resp):
        resp = '' if not resp.text else resp.json()
        ErrorPopup('Record could not be added: ' + str(resp))

    def show_input_error(self):
        ErrorPopup('Some input fields are missing')

    def record_added(self, resp):
        SuccessPopup('Record added')
        self.clear_fields()

    def record_deleted(self, resp):
        SuccessPopup('Record deleted')
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
