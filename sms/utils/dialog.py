from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty, ListProperty

import os.path

Builder.load_string('''
<OpenFileDialog>:
    file_dialog: fc
    BoxLayout:
        orientation: 'vertical'
        FileChooserIconView:
            id: fc
            size_hint_y: .8
            on_selection: root.update_field(args[0])
        BoxLayout:
            spacing: 10
            size_hint_y: None
            height: 30
            Label:
                text: 'File name'
                text_size: self.size
                halign: 'right'
                valign: 'middle'
            TextInput:
                id: filename_txt
                text: root.file_name
            Spinner:
                values: root.filters
                on_text: root.fc_filter(args[1])
                text_autoupdate: True
        BoxLayout:
            spacing: 10
            size_hint: (None, None)
            size: 200, 30
            pos_hint: {'right': 1}
            Button:
                text: 'Load'
                on_press: root.load()
            Button:
                text: 'Cancel'
                on_press: root.dismiss()

<DragAndDropFileDialog>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        BoxLayout:
            canvas.before:
                Color:
                    rgba: root.text_area_color
                Line:
                    rectangle: self.pos[0], self.pos[1], self.width, self.height
                    dash_offset: 9
                    dash_length: 8
            id: drag_area
            Label:
                text: 'Drag Area'
                font_size: sp(48)
                opacity: .5
        Button:
            text: 'Select File'
            size_hint: .4, .1
            pos_hint: {'center_x': .5}
            on_press: root.open_file_dialog()
''')


class OpenFileDialog(Popup):
    file_name = StringProperty()
    file_dialog = ObjectProperty()
    filters = ListProperty()
    selected_path = StringProperty()

    def __init__(self, filter_dict=None, **kwargs):
        super(OpenFileDialog, self).__init__(**kwargs)
        self.title = 'Open'
        self.auto_dismiss = False
        self.size_hint = (.6, .8)

        self.filter_dict = filter_dict if filter_dict else {'All Files': ['*']}
        self.filters = self.filter_dict.keys()
        self.ids['fc'].path = os.path.expanduser('~')
        self.selected_path = ''

    def update_field(self, instance):
        if instance.selection:
            self.file_name = os.path.basename(instance.selection[0])
        else:
            self.file_name = ''

    def on_selected_path(self, instance, value):
        self.file_name = os.path.basename(value)

    def load(self, *args):
        if self.file_dialog.selection:
            self.selected_path = self.file_dialog.selection[0]
            self.dismiss()
        elif self.ids['filename_txt'].text:
            file_paths = list(filter(os.path.isfile, self.file_dialog.files))
            files = list(map(os.path.basename, file_paths))
            if self.ids['filename_txt'].text in files:
                self.selected_path = file_paths[files.index(self.ids['filename_txt'].text)]
                self.dismiss()

    def load_file(self):
        if self.selected_path:
            with open(self.selected_path) as fd:
                data = fd.read()
            return data
        else:
            return ''

    def fc_filter(self, key):
        self.file_dialog.filters = self.filter_dict[key]


class DragAndDropFileDialog(Popup):
    text_area_color = ListProperty([])

    def __init__(self, filter_dict=None, **kwargs):
        super(DragAndDropFileDialog, self).__init__(**kwargs)
        self.title = 'Open'
        self.size_hint = (.6, .8)
        self.selected_path = ''
        self.filter_dict = filter_dict
        self.text_area_color = (.2, .65, .83, 1)

        self.dialog = OpenFileDialog(filter_dict=filter_dict)
        self.dialog.bind(on_dismiss=self.select_path_from_file_dialog)

        Window.bind(on_dropfile=self.validate_drop)
        Window.bind(mouse_pos=self.change_text_area_color)

    def validate_drop(self, instance, filepath):
        if self.ids['drag_area'].collide_point(*instance.mouse_pos):
            self.select_path(filepath)
            self.dismiss()

    def select_path(self, filepath):
        self.selected_path = filepath.decode('utf-8')

    def select_path_from_file_dialog(self, instance):
        self.selected_path = instance.selected_path
        self.dismiss()

    def open_file_dialog(self, *args):
        self.dialog.open()

    def change_text_area_color(self, instance, pos):
        if self.ids['drag_area'].collide_point(*pos):
            self.text_area_color = (.2, .65, .83, 1)
        else:
            self.text_area_color = (.2, .65, .83, .5)


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.button import Button

    dialog = DragAndDropFileDialog()
    btn = Button(text='Open file dialog', on_press=dialog.open)

    runTouchApp(btn)
