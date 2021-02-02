from kivy.lang import Builder
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
''')


class OpenFileDialog(Popup):
    file_name = StringProperty()
    file_dialog = ObjectProperty()
    filters = ListProperty()

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


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.button import Button

    dialog = OpenFileDialog()
    btn = Button(text='Open file dialog', on_press=dialog.open)

    runTouchApp(btn)
