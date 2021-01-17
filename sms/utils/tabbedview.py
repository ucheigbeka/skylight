import os
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.properties import ObjectProperty, StringProperty


Builder.load_string('''
#:import NoTransition kivy.uix.screenmanager.NoTransition

<CustomTabbedPanelContent>:
    sm: sm
    orientation: 'vertical'
    ScreenManager:
        id: sm
        transition: NoTransition()
    BoxLayout:
        size_hint: None, None
        size: 500, 35
        ImageButton:
            source: os.path.join(root.base_dir, 'icons', 'icons8-back-64.png')
            on_press: root.prev_screen()
        ImageButton:
            source: os.path.join(root.base_dir, 'icons', 'icons8-next-page-64.png')
            on_press: root.next_screen()
        TextInput:
            text: root.scr_text
            multiline: False
            input_filter: 'int'
            on_text_validate:
                if 0 < int(self.text) <= len(sm.screens): sm.current = sm.screen_names[int(self.text) - 1]
                else: self.text = str(sm.screen_names.index(sm.current) + 1)
        Label:
            text: '/'
            text_size: self.texture_size
        TextInput
            disabled: True
            text: str(len(sm.screens))
            multiline: False

<CustomTabbedPanelHeader>:
    close_lbl: close_lbl
    Label:
        id: close_lbl
        text: 'x'
        on_touch_down: root.close_tab(args[1])
        pos: self.parent.x + self.parent.width - self.width, self.parent.y
        size: self.texture_size[0], self.parent.height
        padding_x: 10
''')


class CustomTabbedPanelContent(BoxLayout):
    sm = ObjectProperty(None)
    scr_text = StringProperty()
    base_dir = StringProperty(os.path.dirname(__file__))

    def __init__(self, **kwargs):
        super(CustomTabbedPanelContent, self).__init__(**kwargs)
        try:
            self.scr_text = self.sm.screen_names.index(self.sm.current) + 1
        except ValueError:
            self.scr_text = '1'

    def prev_screen(self):
        index = self.sm.screen_names.index(self.sm.current)
        if index > 0:
            self.sm.current = self.sm.screen_names[index - 1]
            self.scr_text = str(index)

    def next_screen(self):
        index = self.sm.screen_names.index(self.sm.current)
        if index < len(self.sm.screen_names) - 1:
            self.sm.current = self.sm.screen_names[index + 1]
            self.scr_text = str(index + 2)


class CustomTabbedPanelHeader(TabbedPanelHeader):
    close_lbl = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CustomTabbedPanelHeader, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.highlight_lbl)
        content_obj = CustomTabbedPanelContent()
        self.sm = content_obj.sm
        self.content = content_obj

    def add_screen(self, screen):
        self.sm.add_widget(screen)

    def highlight_lbl(self, instance, value):
        pos = self.to_widget(*value)
        if self.close_lbl.collide_point(*pos):
            self.close_lbl.color = [1, .5, 0, 1]
        else:
            self.close_lbl.color = [1, 1, 1, 1]

    def close_tab(self, touch):
        if self.close_lbl.collide_point(*touch.pos):
            if self.parent.tabbed_panel.current_tab == self:
                tabs = self.parent.tabbed_panel.tab_list
                if len(tabs) == 1:
                    # exit out of reports screen
                    self.parent.tabbed_panel.clear_widgets()
                else:
                    index = tabs.index(self)
                    index = index - 1 if index > 0 else index + 1
                    self.parent.tabbed_panel.switch_to(tabs[index])
            self.reset_cursor()
            self.parent.tabbed_panel.remove_widget(self)

    def reset_cursor(self):
        for prev_screen in self.sm.screens:
            if hasattr(prev_screen, 'cursor_change_event'):
                Clock.unschedule(prev_screen.cursor_change_event)
        Window.set_system_cursor('arrow')


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.tabbedpanel import TabbedPanel
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.screenmanager import Screen

    Builder.load_string('''
        #:import os os
        #:import ImageButton imagebutton.ImageButton
    ''')

    tp = TabbedPanel(do_default_tab=False)
    tph_1 = CustomTabbedPanelHeader(text='tab 1')
    tph_2 = CustomTabbedPanelHeader(text='tab 2')
    tph_3 = CustomTabbedPanelHeader(text='tab 3')

    s1 = Screen(name='Screen 1')
    s2 = Screen(name='Screen 2')
    s3 = Screen(name='Screen 3')

    s1.add_widget(Label(text='Hello world by Uche'))
    s2.add_widget(Button(text='Press me :-)'))
    s3.add_widget(Label(text='Another Hello world by Uche'))

    tph_1.add_screen(s1)
    tph_1.add_screen(s2)
    tph_1.add_screen(s3)

    tp.add_widget(tph_1)
    tp.add_widget(tph_2)
    tp.add_widget(tph_3)

    runTouchApp(tp)
