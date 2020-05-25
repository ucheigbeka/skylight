import os
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ListProperty,\
    AliasProperty, ObjectProperty, DictProperty, StringProperty
from kivy.core.clipboard import Clipboard

try:
    from sms.utils.label import CustomLabel
    from sms.utils.popups import ErrorPopup
except ImportError:
    from label import CustomLabel
    from popups import ErrorPopup

Builder.load_string('''
<HeaderLabel>:
    canvas.before:
        Color:
            rgba: 0, .4, .4, 1
        Rectangle:
            pos: self.pos
            size: self.size

<DataViewerInput>:
    height: 50
    multiline: False
    write_tab: False

<DataViewerLabel>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, .8
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0, 0, 0, 1
        Line:
            points: self.pos[0], self.pos[1], self.pos[0], self.pos[1] + self.height, self.pos[0] + self.width, self.pos[1] + self.height, self.pos[0] + self.width, self.pos[1]
            width: 1
            cap: 'square'
            joint: 'miter'
            close: True
    text_size: self.size
    valign: 'middle'
    halign: 'center'
    color: 0, 0, 0, 1

<DataViewer>:
    rv: rv
    orientation: 'vertical'
    RecycleView:
        viewclass: 'HeaderLabel'
        data: root.viewer_header
        size_hint_y: None
        height: header_layout.height
        size_hint_x: None
        width: content_layout.minimum_width
        RecycleGridLayout:
            id: header_layout
            cols: root.cols
            size_hint_y: None
            default_size: dp(100), dp(35)
            default_size_hint: None, None
            height: self.minimum_height
    RecycleView:
        id: rv
        viewclass: 'DataViewerInput'
        data: root.data_for_widget
        size_hint_x: None
        width: content_layout.minimum_width
        RecycleGridLayout:
            id: content_layout
            cols: root.cols
            size_hint_y: None
            default_size: dp(100), dp(35)
            default_size_hint: None, None
            height: self.minimum_height

<DataViewer2>:
    dv: dv
    _data: dv._data
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: None
        width: sp(50)
        HeaderLabel:
            text: 'S/N'
            size_hint_y: None
            height: dp(35)
        RecycleView:
            viewclass: 'HeaderLabel'
            data: [{'text': str(i), 'valign': 'middle'} for i in range(int(len(root._data)))]
            scroll_y: dv.rv.scroll_y
            do_scroll_y: False
            RecycleGridLayout:
                cols: 1
                size_hint_y: None
                default_size: sp(50), dp(35)
                default_size_hint: None, None
                height: self.minimum_height
    DataViewer:
        id: dv
        cols: root.cols
        widths: root.widths
        prop: root.prop
        headers: root.headers
        _data: root._data

<ExtendableDataViewer>:
    orientation: 'vertical'
    DataViewer:
        id: dv
        cols: root.cols
        widths: root.widths if root.widths else [100] * self.cols
        prop: root.prop
        headers: root.headers
        _data: root.data if root.data else [[''] * self.cols]
        size_hint_x: None
        width: self.rv.width
    BoxLayout:
        size_hint: None, None
        width: dv.rv.width if dv.rv.width else root.width
        height: dp(50)
        Button:
            text: '+'
            on_press: dv.add_data([''] * root.cols)
        Button:
            text: '-'
            on_press: dv.remove_data()
        ImageButton:
            source: os.path.join(root.base_dir, 'icons', 'paste.png')
            on_press: dv.paste()
        Button:
            text: 'clear'
            on_press: dv.clear()

<ExtendableDataViewer2>:
    dv: dv
    orientation: 'vertical'
    DataViewer2:
        id: dv
        cols: root.cols
        widths: root.widths if root.widths else [100] * self.cols
        prop: root.prop
        headers: root.headers
        _data: root.data if root.data else [[''] * self.cols]
        size_hint_x: None
        width: self.dv.rv.width
    BoxLayout:
        size_hint: None, None
        width: dv.dv.rv.width + 50 if dv.dv.rv.width else root.width
        height: dp(50)
        Button:
            text: '+'
            on_press: dv.dv.add_data([''] * root.cols)
        Button:
            text: '-'
            on_press: dv.dv.remove_data()
        ImageButton:
            source: os.path.join(root.base_dir, 'icons', 'paste.png')
            on_press: dv.dv.paste()
        Button:
            text: 'clear'
            on_press: dv.dv.clear()
''')


class HeaderLabel(CustomLabel):
    pass


class DataViewerInput(TextInput):
    """
        Viewclass for the recycleview widget that's
        intended for accepting and displaying data
    """
    root = ObjectProperty(None)
    index = NumericProperty(0)
    col_num = NumericProperty(0)

    def on_focus(self, instance, value):
        if not value:
            try:
                self.root._data[self.index][self.col_num] = self.text
            except IndexError as err:
                print(err)


class DataViewerLabel(Label):
    """
        Viewclass for the recycleview widget that's
        intended for only displaying data
    """
    root = ObjectProperty(None)
    index = NumericProperty(0)
    col_num = NumericProperty(0)


class DataViewer(BoxLayout):
    cols = NumericProperty(0)
    _data = ListProperty()
    headers = ListProperty()
    widths = ListProperty()
    prop = DictProperty()
    rv = ObjectProperty(None)

    def load_header(self):
        viewer_header = []
        if len(self.headers) != self.cols:
            #raise ValueError
            pass
        for i in range(len(self.headers)):
            viewer_header.append(
                {'text': self.headers[i], 'width': self.widths[i], 'valign': 'middle'})
        return viewer_header

    def load_data(self):
        data_for_widget = []
        for index, row in enumerate(self._data):
            if len(row) != self.cols:
                ErrorPopup('Error parsing data')
            for col_num, col in enumerate(row):
                prop = {'index': index, 'col_num': col_num, 'text': str(
                    col), 'width': self.widths[col_num], 'root': self}
                prop.update(self.prop)
                data_for_widget.append(prop)
        return data_for_widget

    viewer_header = AliasProperty(load_header, bind=['headers'])
    data_for_widget = AliasProperty(load_data, bind=['_data'])

    def add_data(self, data, pos=-1):
        if pos != -1:
            self._data.insert(pos, data)
        else:
            self._data.append(data)

    def remove_data(self):
        if len(self._data) > 1:
            self._data.pop()
        elif len(self._data) == 1:
            self._data = [[''] * self.cols]

    def clear(self):
        self._data = [[''] * self.cols]

    def paste(self):
        str_list = Clipboard.paste().split(os.linesep)
        data = []
        for row in str_list:
            data.append(row.split('\t'))
        if data[-1] == ['']:
            data.pop()
        if len(self._data) == 1 and self._data[0] == [''] * self.cols:
            self._data = data
        else:
            self._data.extend(data)


class DataViewer2(BoxLayout):
    cols = NumericProperty(1)
    _data = ListProperty()
    headers = ListProperty()
    widths = ListProperty()
    prop = DictProperty()
    dv = ObjectProperty(None)


class ExtendableDataViewer(BoxLayout):
    cols = NumericProperty(1)
    data = ListProperty()
    headers = ListProperty()
    widths = ListProperty()
    prop = DictProperty()
    base_dir = StringProperty(os.path.dirname(__file__))

    def __init__(self, **kwargs):
        super(ExtendableDataViewer, self).__init__(**kwargs)


class ExtendableDataViewer2(BoxLayout):
    cols = NumericProperty(1)
    data = ListProperty()
    headers = ListProperty([''])
    widths = ListProperty()
    prop = DictProperty()
    base_dir = StringProperty(os.path.dirname(__file__))
    dv = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ExtendableDataViewer2, self).__init__(**kwargs)


if __name__ == '__main__':
    from kivy.app import runTouchApp

    Builder.load_string('''
        #:import ImageButton imagebutton.ImageButton
        #:import CustomLabel label.CustomLabel
        #:import os os
        ''')

    # runTouchApp(ExtendableDataViewer2(cols=3, data=[[x, x + 1, x + 2] for x in range(0, 200, 3)], headers=[
    #             'Column #1', 'Column #2', 'Column #3'], widths=[100, 200, 300], prop={'disabled': True}))

    runTouchApp(ExtendableDataViewer2(cols=3, headers=[
                'Column #1', 'Column #2', 'Column #3'], widths=[100, 200, 300], prop={'disabled': True}))

    # runTouchApp(DataViewer(cols=3, widths=[100, 200, 300], prop={'disabled': True}, _data=[[1,2,3]]))
