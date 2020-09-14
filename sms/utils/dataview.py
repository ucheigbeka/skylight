import os
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import NumericProperty, ListProperty,\
    AliasProperty, ObjectProperty, DictProperty, StringProperty,\
    BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.factory import Factory
from kivy.core.clipboard import Clipboard

try:
    from sms.utils.label import CustomLabel
    from sms.utils.popups import ErrorPopup
except ImportError:
    from label import CustomLabel
    from popups import ErrorPopup

Builder.load_string('''
#:set DEFAULT_SIZE (dp(100), dp(35))
#:set DEFAULT_SIZE_HEADER (dp(50), dp(35))

<DataViewerInput>:
    height: 50
    multiline: False
    write_tab: False
    background_color: (.2, .2, .7, 1) if root.is_selected else (1, 1, 1, 1)

<DataViewerLabel>:
    canvas.before:
        Color:
            rgba: (.2, .2, .7, 1) if root.is_selected else (1, 1, 1, 1)
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
    selectable_grid: content_layout
    orientation: 'vertical'
    RecycleView:
        viewclass: 'HeaderLabel'
        data: root.viewer_header
        size_hint: None, None
        height: header_layout.height
        width: content_layout.minimum_width
        RecycleGridLayout:
            id: header_layout
            cols: root.cols
            size_hint_y: None
            default_size: DEFAULT_SIZE
            default_size_hint: None, None
            height: self.minimum_height
    RecycleView:
        id: rv
        viewclass: 'DataViewerInput'
        # viewclass: 'DataViewerLabel'
        data: root.data_for_widget
        size_hint_x: None
        width: content_layout.minimum_width
        SelectableRecycleGridLayout:
            id: content_layout
            cols: root.cols
            size_hint_y: None
            default_size: DEFAULT_SIZE
            default_size_hint: None, None
            height: self.minimum_height

<DataViewer2>:
    dv: dv
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: None if not dv.weightings else .06
        width: DEFAULT_SIZE_HEADER[0]
        HeaderLabel:
            text: 'S/N'
            size_hint: None, None
            width: self.parent.width
            height: DEFAULT_SIZE_HEADER[1]
        RecycleView:
            viewclass: 'SelectableLabel'
            data: [{'text': str(i), 'valign': 'middle'} for i in range(int(len(dv._data)))]
            scroll_y: dv.rv.scroll_y
            do_scroll_y: False
            SelectableRecycleGridLayout:
                cols: 1
                size_hint_y: None
                default_size: DEFAULT_SIZE_HEADER
                default_size_hint: (None, None) if not dv.weightings else (1, None)
                height: self.minimum_height
    DataViewer:
        id: dv
        cols: root.cols
        weightings: root.weightings
        widths: root.widths
        prop: root.prop
        headers: root.headers
        _data: root._data
        selectable: root.selectable
        multiselection: root.multiselection

<ExtendableDataViewer>:
    orientation: 'vertical'
    DataViewer:
        id: dv
        cols: root.cols
        weightings: root.weightings
        widths: root.widths if root.widths else [100] * self.cols
        prop: root.prop
        headers: root.headers
        _data: root.data if root.data else [[''] * self.cols]
    BoxLayout:
        size_hint: (None, None) if not dv.weightings else (1, None)
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
        weightings: root.weightings
        widths: root.widths if root.widths else [100] * self.cols
        prop: root.prop
        headers: root.headers
        _data: root.data if root.data else [[''] * self.cols]
        selectable: root.selectable
        multiselection: root.multiselection
    BoxLayout:
        size_hint: (None, None) if not dv.weightings else (1, None)
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


class SelectableLabel(RecycleDataViewBehavior, FocusBehavior, Factory.HeaderLabel):
    dv = ObjectProperty()
    index = NumericProperty()

    def refresh_view_attrs(self, rv, index, data):
        self.dv = rv.parent.parent.dv
        self.index = index
        super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dv.toggle_row_selection_state(self.index)
            return True

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.dv.toggle_row_selection_state(self.index)
            return True


class DataViewerInput(RecycleDataViewBehavior, TextInput):
    """
        Viewclass for the recycleview widget that's
        intended for accepting and displaying data
    """
    root = ObjectProperty(None)
    index = NumericProperty(0)
    col_num = NumericProperty(0)
    is_selected = BooleanProperty(False)
    _index = NumericProperty()

    # Reverse comment of this section if experiencing performance issues.
    # on_focus, more efficient, but doesn't capture user inputs in
    # certain scenarios
    def on_text(self, instance, value):
        try:
            self.root._data[self.index][self.col_num] = value
        except (AttributeError, IndexError):
            pass

    # def on_focus(self, instance, value):
    #     if not value:
    #         try:
    #             self.root._data[self.index][self.col_num] = self.text
    #         except IndexError as err:
    #             print(err)

    def refresh_view_attrs(self, rv, index, data):
        self._index = index
        super(DataViewerInput, self).refresh_view_attrs(rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        self.is_selected = is_selected


class DataViewerLabel(RecycleDataViewBehavior, Label):
    """
        Viewclass for the recycleview widget that's
        intended for only displaying data
    """
    root = ObjectProperty(None)
    index = NumericProperty(0)
    col_num = NumericProperty(0)
    is_selected = BooleanProperty(False)
    _index = NumericProperty()

    def refresh_view_attrs(self, rv, index, data):
        self._index = index
        super(DataViewerLabel, self).refresh_view_attrs(rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        self.is_selected = is_selected


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    def __init__(self, **kwargs):
        self.multiselect = True
        super(SelectableRecycleGridLayout, self).__init__(**kwargs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super(SelectableRecycleGridLayout, self).keyboard_on_key_down(window, keycode, text, modifiers)
        root = self.parent.parent.parent.dv
        if len(modifiers) == 1 and root.selectable:
            if modifiers[0] == 'ctrl' and keycode[1] == 'down':
                prev_index = root.selected_indexes[-1]
                root.toggle_row_selection_state(prev_index + 1)
            elif modifiers[0] == 'ctrl' and keycode[1] in 'up':
                prev_index = root.selected_indexes[-1]
                root.toggle_row_selection_state(prev_index - 1)
        elif keycode[1] == 'numpad9':
            root.pan_up()
        elif keycode[1] == 'numpad3':
            root.pan_down()

    def on_focus(self, instance, value):
        if not value:
            try:
                root = self.parent.parent.parent.dv
            except AttributeError:
                root = self.parent.parent
            if root.selectable and not root.multiselection and root.selected_indexes:
                index = root.selected_indexes.pop()
                root.deselect(index)


class DataViewer(BoxLayout):
    cols = NumericProperty(0)
    _data = ListProperty()
    headers = ListProperty()
    widths = ListProperty()
    weightings = ListProperty()
    prop = DictProperty()
    rv = ObjectProperty(None)
    selectable_grid = ObjectProperty(None)

    multiselection = BooleanProperty(False)
    selectable = BooleanProperty(False)
    selected_indexes = ListProperty()

    def load_header(self):
        viewer_header = []
        if len(self.headers) != self.cols:
            #raise ValueError
            pass
        for i in range(len(self.headers)):
            if bool(self.weightings):
                width = self.width * self.weightings[i]
            else:
                width = self.widths[i]
            viewer_header.append(
                {'text': self.headers[i], 'width': width, 'valign': 'middle'})
        return viewer_header

    def load_data(self):
        data_for_widget = []
        for index, row in enumerate(self._data):
            if len(row) != self.cols:
                ErrorPopup('Error parsing data')
            for col_num, col in enumerate(row):
                if bool(self.weightings):
                    width = self.width * self.weightings[col_num]
                else:
                    width = self.widths[col_num]
                prop = {'index': index, 'col_num': col_num, 'text': str(
                    col), 'width': width, 'root': self}
                for attr, val in self.prop.items():
                    if isinstance(val, list) and len(val) == self.cols:
                        prop[attr] = val[col_num]
                    else:
                        prop[attr] = val
                data_for_widget.append(prop)
        return data_for_widget

    viewer_header = AliasProperty(load_header, bind=['headers', 'width'])
    data_for_widget = AliasProperty(load_data, bind=['_data', 'width'])

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = [row[:] for row in data]

    def set_viewclass(self, viewclass):
        self.rv.viewclass = viewclass

    def add_data(self, data, pos=-1):
        if pos != -1:
            self._data.insert(pos, data)
        else:
            self._data.append(data)

    def remove_data(self):
        if self.selected_indexes:
            count = 0
            selected_indexes = self.selected_indexes[:]
            selected_indexes.sort(reverse=True)
            while selected_indexes:
                idx = selected_indexes.pop()
                self._data.pop(idx - count)
                count += 1
            self.selectable_grid.clear_selection()
            self.selected_indexes = []
            if not len(self._data):
                self._data = [[''] * self.cols]
        else:
            if len(self._data) > 1:
                self._data.pop()
            elif len(self._data) == 1:
                self._data = [[''] * self.cols]

    def clear(self):
        self._data = [[''] * self.cols]
        if self.selectable:
            self.selectable_grid.clear_selection()
            self.selected_indexes = []

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

    def get_view_by_cord(self, row_idx, col_idx):
        index = row_idx * self.cols + col_idx
        return self.get_view_by_index(index)

    def get_view_by_index(self, index):
        curr_views = self.ids['content_layout'].children
        view = None
        for view in curr_views:
            if view._index == index:
                break
        return view

    def get_selected_items(self):
        selected_items = []
        for idx in self.selected_indexes:
            selected_items.append(self._data[idx])

        return selected_items

    def toggle_row_selection_state(self, index):
        if self.selectable:
            if index < 0 or index > len(self._data) - 1:
                return
            if not self.multiselection and self.selected_indexes:
                prev_index = self.selected_indexes.pop()
                self.deselect(prev_index)
            if index in self.selected_indexes:
                self.deselect(index)
                self.selected_indexes.remove(index)
            else:
                self.select(index)
                self.selected_indexes.append(index)

    def select(self, index):
        start = index * self.cols
        idxes = [view._index for view in self.selectable_grid.children]
        first_index = min(idxes)
        last_index = self.selectable_grid.children[self.cols - 1]._index
        if start >= last_index:
            self.scroll_down()
        elif start <= first_index:
            self.scroll_up()
        for idx in range(start, start + self.cols):
            self.selectable_grid.select_node(idx)

    def deselect(self, index):
        start = index * self.cols
        for idx in range(start, start + self.cols):
            self.selectable_grid.deselect_node(idx)

    def scroll_up(self):
        self.rv.scroll_y += (1.0 / len(self._data)) * 2

    def scroll_down(self):
        self.rv.scroll_y -= (1.0 / len(self._data)) * 2

    def pan_up(self):
        rows = (len(self.selectable_grid.children) - 1) / self.cols
        for i in range(int(rows / 2)):
            self.scroll_up()

    def pan_down(self):
        rows = (len(self.selectable_grid.children) - 1) / self.cols
        for i in range(int(rows / 2)):
            self.scroll_down()


class DataViewer2(BoxLayout):
    cols = NumericProperty(1)
    _data = ListProperty()
    headers = ListProperty()
    weightings = ListProperty()
    widths = ListProperty()
    prop = DictProperty()
    dv = ObjectProperty(None)

    selectable = BooleanProperty(False)
    multiselection = BooleanProperty(False)


class ExtendableDataViewer(BoxLayout):
    cols = NumericProperty(1)
    data = ListProperty()
    headers = ListProperty()
    widths = ListProperty()
    weightings = ListProperty()
    prop = DictProperty()
    base_dir = StringProperty(os.path.dirname(__file__))

    def get_dataviewer(self):
        return self.ids['dv']


class ExtendableDataViewer2(BoxLayout):
    cols = NumericProperty(1)
    data = ListProperty()
    headers = ListProperty([''])
    widths = ListProperty()
    weightings = ListProperty()
    prop = DictProperty()
    base_dir = StringProperty(os.path.dirname(__file__))
    dv = ObjectProperty(None)

    selectable = BooleanProperty(False)
    multiselection = BooleanProperty(False)

    def get_dataviewer(self):
        return self.ids['dv'].dv


if __name__ == '__main__':
    from kivy.app import runTouchApp

    Builder.load_string('''
        #:import ImageButton imagebutton.ImageButton
        #:import CustomLabel label.CustomLabel
        #:import os os
        ''')

    # runTouchApp(ExtendableDataViewer2(cols=3, data=[[x, x + 1, x + 2] for x in range(0, 200, 3)], headers=[
    #             'Column #1', 'Column #2', 'Column #3'], widths=[100, 200, 300], prop={'disabled': True}))

    runTouchApp(ExtendableDataViewer2(
        cols=3,
        widths=[100, 200, 300],
        weightings=[.2, .2, .6],
        headers=['Column #1', 'Column #2', 'Column #3'],
        data=[[i, i + 1, i + 2] for i in range(0, 201, 3)],
        selectable=True,
        multiselection=0
    ))
