import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from sms import urlTo
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup
from sms.utils.dialog import OpenFileDialog

from xlrd import open_workbook, XL_CELL_NUMBER

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'result_entry.kv')
Builder.load_file(kv_path)

HEADER = ['COURSE_CODE', 'SESSION', 'MATNO', 'SCORE']


def parse_xl_sheet(sheet):
    data = []
    if sheet.ncols != 4:
        raise ValueError('err')
    header = list(map(lambda x: x.upper(), sheet.row_values(0)))
    sequence = []
    for val in header:
        sequence.append(HEADER.index(val))
    for row_idx in range(1, sheet.nrows):
        row = [0] * 4
        for col_idx in range(sheet.ncols):
            index = sequence[col_idx]
            cell = sheet.cell(row_idx, col_idx)
            if cell.ctype == XL_CELL_NUMBER:
                row[index] = int(cell.value)
            else:
                row[index] = str(cell.value)
        data.append(row)

    return data


class LoadPopupContent(BoxLayout):
    pass


class LoadPopup(Popup):
    def __init__(self, **kwargs):
        super(LoadPopup, self).__init__(**kwargs)
        self.title = 'Load file'
        self.content = LoadPopupContent()
        self.size_hint = (.2, .18)

        self.open()


class Result_Entry(FormTemplate):
    edv = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Result_Entry, self).__init__(**kwargs)

    def strip_data(self):
        text = self.text_input.text.strip().split('\n')
        data = []
        for row in text:
            res = row.strip().split()
            if len(res) != 4:
                return None
            data.append(res)
        return data

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        filter_dict = {
            'Excel Files (*.xls, *.xlsx)': ['*.xls', '*.xlsx'],
            'Text Document (*.txt)': ['*.txt'], 'All Files': ['*']
        }
        dialog = OpenFileDialog(filter_dict=filter_dict)
        dialog.bind(on_dismiss=self.update_dataview)
        dialog.open()

    def parse_txt(self, instance):
        try:
            str_list = instance.load_file().split('\n')
            data, str_len = [], len(str_list)
            for idx in range(str_len):
                row = str_list[idx]
                _row = row.split('\t')
                if len(_row) != 4 and idx != str_len - 1:
                    raise ValueError
                data.append(_row)
            if data[-1] == ['']:
                data.pop()
            if len(self.edv.data) == 1 and self.edv.data[0] == [''] * 4:
                self.edv.data = data
            else:
                self.edv.data.extend(data)
        except ValueError:
            ErrorPopup('Error parsing {}'.format(instance.file_name))

    def parse_xl(self, filepath):
        try:
            xl_workbook = open_workbook(filepath)
            data = []
            for sheet in xl_workbook.sheets():
                data.extend(parse_xl_sheet(sheet))
            if len(self.edv.data) == 1 and self.edv.data[0] == [''] * 4:
                self.edv.data = data
            else:
                self.edv.data.extend(data)
        except ValueError:
            ErrorPopup('Error parsing {}'.format(os.path.basename(filepath)))

    def update_dataview(self, instance):
        if instance.selected_path:
            ext = os.path.splitext(instance.selected_path)[1]
            if ext in ['.xls', '.xlsx']:
                self.parse_xl(instance.selected_path)
            else:
                self.parse_txt(instance)

    def clear_dataview(self, resp):
        resp = resp.json()
        if resp:
            err_msg = '\n'.join(resp)
            ErrorPopup(err_msg, title='Alert')
        self.edv.data = [[''] * 4]

    def upload(self, *args):
        url = urlTo('results')
        data = self.edv.data if self.edv.data else self.edv.dv._data
        if data and data != [['','','','']]:
            AsyncRequest(url, data=data, method='POST',
                         on_success=self.clear_dataview)
        else:
            ErrorPopup('Error parsing results. Check your input')
