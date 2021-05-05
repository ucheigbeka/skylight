import os
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty

from sms import urlTo, get_assigned_level, root
from sms.forms.template import FormTemplate
from sms.utils.asyncrequest import AsyncRequest
from sms.utils.popups import ErrorPopup, PopupBase
from sms.utils.dialog import DragAndDropFileDialog

from xlrd import open_workbook, XL_CELL_NUMBER

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'result_entry_multiple.kv')
Builder.load_file(kv_path)

HEADER = ['COURSE_CODE', 'SESSION', 'MATNO', 'SCORE']


def unload():
    Builder.unload_file(kv_path)


def parse_xl_header(sheet):
    sequence, headers = [], sheet.row_values(0)
    ignore_idxs = []
    try:
        for idx in range(len(headers)):
            cap_header = headers[idx].strip().upper()
            if cap_header == 'S/N':
                sequence.append('')
                ignore_idxs.append(idx)
            else:
                if cap_header in ['COURSE', 'CODE', 'COURSE CODE', 'COURSE-CODE']:
                    cap_header = HEADER[0]
                elif cap_header in ['MAT.NO', 'MAT. NO', 'MAT NO']:
                    cap_header = HEADER[2]
                sequence.append(HEADER.index(cap_header))
    except IndexError:
        return [], []

    return sequence, ignore_idxs


def parse_xl_sheet(sheet, sequence, ignore_idxs):
    data = []
    if sheet.ncols not in [4, 5]:
        raise ValueError('err')
    start = 1 if sequence else 0
    for row_idx in range(start, sheet.nrows):
        row = [0] * 4
        for col_idx in range(sheet.ncols):
            if col_idx in ignore_idxs:
                continue
            index = sequence[col_idx]
            cell = sheet.cell(row_idx, col_idx)
            if cell.ctype == XL_CELL_NUMBER:
                row[index] = int(cell.value)
            else:
                row[index] = str(cell.value).strip()
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


class XlPopupCheckBox(RecycleDataViewBehavior, CheckBox):
    root = ObjectProperty(None)
    index = 0

    def on_active(self, ins, value):
        self.root.sheets_parse_sequence[self.index] = int(value)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        super(XlPopupCheckBox, self).refresh_view_attrs(rv, index, data)


class XlPopupContent(BoxLayout):
    title = StringProperty()
    dismiss = BooleanProperty(False)
    sheets_parse_sequence = ListProperty([])
    open_func = None

    def __init__(self, data, **kwargs):
        super(XlPopupContent, self).__init__(**kwargs)
        cboxes, lbls = zip(*data)
        self.sheets_parse_sequence = list(cboxes)
        data_for_rv1, data_for_rv2 = [], []
        for idx in range(len(cboxes)):
            data_for_rv1.append({'active': bool(cboxes[idx]), 'root': self})
            data_for_rv2.append({'text': str(lbls[idx]), 'root': self})

        self.title = str(len(data)) + ' Sheets Found'
        self.ids['rv1'].data = data_for_rv1
        self.ids['rv2'].data = data_for_rv2

    def on_sheets_parse_sequence(self, instance, value):
        btn_open = self.ids['btn_open']
        if 1 not in self.sheets_parse_sequence:
            btn_open.disabled = True
        else:
            btn_open.disabled = False

    def open(self, **kwargs):
        if self.open_func:
            self.open_func(self.sheets_parse_sequence)
            self.dismiss = True

    def set_open_callback(self, open_func):
        self.open_func = open_func


class XlPopup(PopupBase):
    def __init__(self, sheet_names, open_func, **kwargs):
        self.title = 'Alert'
        self.auto_dismiss = False
        data = list(zip([0] * len(sheet_names), sheet_names))
        self.content = XlPopupContent(data)
        self.content.bind(dismiss=lambda ins, val: self.dismiss())
        self.content.set_open_callback(open_func)
        self.size_hint = (.4, .8)
        super(XlPopup, self).__init__(**kwargs)


class ResultEntryMultiple(FormTemplate):
    edv = ObjectProperty(None)
    xl_workbook = None
    err_msg = ''

    title = 'Result Entry'

    def __init__(self, **kwargs):
        super(ResultEntryMultiple, self).__init__(**kwargs)
        self.edv.get_dataviewer().bind(_data=self.data_changed)

    def data_changed(self, instance, value):
        if value == [[''] * 4]:
            self.err_msg = ''

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap and self.err_msg:
            self.show_error_popup()
        return super(ResultEntryMultiple,self).on_touch_down(touch)

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
        dialog = DragAndDropFileDialog(filter_dict=filter_dict)
        dialog.bind(on_dismiss=self.update_dataview)
        dialog.open()

    def parse_txt(self, dialog):
        try:
            str_list = dialog.load_file().split('\n')
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
            ErrorPopup('Error parsing {}'.format(dialog.file_name))

    def open_workbook(self, filepath):
        self.xl_workbook = open_workbook(filepath)
        self.xl_workbook.filepath = filepath
        if self.xl_workbook.nsheets > 1:
            XlPopup(self.xl_workbook.sheet_names(), self.parse_xl)
        else:
            self.parse_xl([1])

    def parse_xl(self, parse_sequence):
        try:
            data = []
            sheets = self.xl_workbook.sheets()
            for idx in range(len(parse_sequence)):
                if parse_sequence[idx]:
                    data.extend(parse_xl_sheet(sheets[idx], *parse_xl_header(sheets[idx])))
            if len(self.edv.data) == 1 and self.edv.data[0] == [''] * 4:
                self.edv.data = data
            else:
                self.edv.data.extend(data)
        except ValueError:
            ErrorPopup('Error parsing {}'.format(os.path.basename(self.xl_workbook.filepath)))
        self.xl_workbook = None

    def update_dataview(self, instance):
        if instance.selected_path:
            ext = os.path.splitext(instance.selected_path)[1]
            if ext in ['.xls', '.xlsx']:
                self.open_workbook(instance.selected_path)
            else:
                self.parse_txt(instance.dialog)

    def clear_dataview(self):
        self.edv.data = [[''] * 4]
        # Refreshs the dataview
        self.edv.data.append([''] * 4)
        self.edv.data = [[''] * 4]
        self.xl_workbook = None
        self.err_msg = ''

    def _strip_data(self, data):
        for idx in range(len(data)):
            for idx2 in range(4):
                data[idx][idx2] = str(data[idx][idx2]).strip()

    def validate_data(self, data):
        if not data:
            return '', False
        for idx in range(len(data)):
            if not data[idx][1].isnumeric() or not data[idx][3].lstrip('-').isnumeric():
                return idx, False
        return '', True

    def upload(self, *args):
        url = urlTo('results')
        dv = self.edv.get_dataviewer()
        list_of_results = dv.get_data()
        self._strip_data(list_of_results)
        idx, is_valid = self.validate_data(list_of_results)
        if is_valid:
            params = {'superuser': True} if root.sm.is_admin else None
            data = {
                'level': get_assigned_level(),
                'list_of_results': list_of_results
            }
            AsyncRequest(url, data=data, params=params, method='POST', on_success=self.show_response)

        else:
            if idx != '':
                ErrorPopup('Error parsing results at index ' + str(idx + 1))
            else:
                ErrorPopup('Error parsing results. Check your input')

    def persist_failures(self, idxs):
        dv = self.edv.get_dataviewer()
        data = dv.get_data()
        new_data = []
        for idx in idxs:
            new_data.append(data[idx - 1])
        dv.set_data(new_data)

    def show_error_popup(self, err_msg=None):
        self.err_msg = err_msg if err_msg else self.err_msg
        ErrorPopup(self.err_msg, title='Alert', size_hint=(.4, .8), auto_dismiss=False)

    def show_response(self, resp):
        resp = resp.json()
        if resp:
            idxs, err_msgs = zip(*resp)
            err_msg = '\n'.join(err_msgs)
            if err_msg == 'Done':
                self.clear_dataview()
            else:
                self.persist_failures(idxs)
            self.show_error_popup(err_msg)
