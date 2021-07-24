from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from sms import urlTo
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import SuccessPopup

Builder.load_string('''
<AdminInfo>:
    BoxLayout:
        orientation: 'vertical'
        GridLayout:
            padding: dp(20)
            spacing: dp(20)
            pos_hint: {'center_x': .5}
            cols: 2
            size_hint: .6, None
            row_default_height: dp(40)
            row_force_default: True
            height: self.minimum_height
            CustomLabel:
                text: 'Vice Chancellor'
                halign: 'left'
            CustomTextInput:
                id: vc
                size_hint_x: 1
            CustomLabel:
                text: 'Chairman, Sub-Committee BCS'
                halign: 'left'
            CustomTextInput:
                id: chairman
                size_hint_x: 1
            CustomLabel:
                text: 'Faculty(Chairman, Sub-Committee BCS)'
                halign: 'left'
            CustomTextInput:
                id: chairmanBCSFaculty
                size_hint_x: 1
            CustomLabel:
                text: 'Dean'
                halign: 'left'
            CustomTextInput:
                id: dean
                size_hint_x: 1
            CustomLabel:
                text: 'Faculty Exam Officer'
                halign: 'left'
            CustomTextInput:
                id: exam_officer
                size_hint_x: 1
            CustomLabel:
                text: 'Head of Department'
                halign: 'left'
            CustomTextInput:
                id: hod
                size_hint_x: 1
            CustomLabel:
                text: 'Number of prize winners'
                halign: 'left'
            CustomTextInput:
                id: prize_winners
                width: dp(200)
                input_filter: 'int'
        RelativeLayout:
            size_hint: 1, .3
            Button:
                text: 'Update'
                size_hint: .2, .18
                pos_hint: {'center_x': .5, 'top': .9}
                background_color: 0, 1, 0, .5
                on_press: root.update()
''')


class AdminInfo(Screen):
    def on_enter(self):
        url = urlTo('dynamic_props')
        AsyncRequest(url, method='GET', on_success=self.populate_info)

    def populate_info(self, resp):
        data = resp.json()

        self.ids['vc'].text = '' if data['ViceChancellor'] is None else data['ViceChancellor']
        self.ids['chairman'].text = '' if data['ChairmanSubCommitteeBCS'] is None else data['ChairmanSubCommitteeBCS']
        self.ids['chairmanBCSFaculty'].text = '' if data['ChairmanSubCommitteeBCS(Faculty)'] is None else data['ChairmanSubCommitteeBCS(Faculty)']
        self.ids['dean'].text = '' if data['Dean'] is None else data['Dean']
        self.ids['exam_officer'].text = '' if data['FacultyExamOfficer'] is None else data['FacultyExamOfficer']
        self.ids['hod'].text = '' if data['HOD'] is None else data['HOD']
        self.ids['prize_winners'].text = '0' if data['NumPrizeWinners'] is None else str(data['NumPrizeWinners'])

    def update(self):
        data = dict()

        data['ViceChancellor'] = self.ids['vc'].text
        data['ChairmanSubCommitteeBCS'] = self.ids['chairman'].text
        data['ChairmanSubCommitteeBCS(Faculty)'] = self.ids['chairmanBCSFaculty'].text
        data['Dean'] = self.ids['dean'].text
        data['FacultyExamOfficer'] = self.ids['exam_officer'].text
        data['HOD'] = self.ids['hod'].text
        data['NumPrizeWinners'] = int(self.ids['prize_winners'].text)

        url = urlTo('dynamic_props')
        AsyncRequest(url, data=data, method='PATCH', on_success=self.submit_success)

    def submit_success(self, resp):
        SuccessPopup('Info updated')
