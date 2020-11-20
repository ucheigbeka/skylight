import os
from kivy.lang import Builder
from kivy.graphics import Color, Ellipse
from kivy.core.text import Label as CoreLabel
from kivy.uix.actionbar import ActionBar, ActionView
from kivy.properties import StringProperty, BooleanProperty, NumericProperty,\
    ObjectProperty

from sms import AsyncRequest, urlTo

Builder.load_string('''
#:import os os

<Separator@Label+ActionItem>:
    size_hint_x: .6

<ActionSwitch@Switch+ActionItem>:
    size_hint_x: .1

<LoginActionView>:
    spacing: dp(20)
    ActionPrevious:
        title: root.title
        with_previous: False
        on_release: root.dispatch('on_previous_btn_pressed')
    ActionButton:
        text: 'Exit'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-close-window-32.png')
        on_press: root.dispatch('on_exit_btn_pressed')

<MainActionView>:
    notification: notification
    spacing: dp(20)
    ActionPrevious:
        title: root.title
        with_previous: root.with_previous
        on_release: root.dispatch('on_previous_btn_pressed')
    ActionButton:
        text: 'Reports'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-business-report-32.png')
        important: True
        on_press: root.dispatch('on_reports_btn_pressed')
    ActionButton:
        text: 'Home'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-home-32.png')
        text: 'home'
        important: True
        on_press: root.dispatch('on_home_btn_pressed')
    ActionButton:
        text: 'Settings'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-settings-32.png')
        important: True
        on_press: root.dispatch('on_settings_btn_pressed')
    Separator:
        important: True
    ActionSwitch:
        id: result_switch
        important: True
        disabled: True
        on_touch_down: root.get_results_edit()
    ActionButton:
        id: notification
        text: 'Notifications'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-bell-32.png')
        on_press: root.dispatch('on_notification_btn_pressed')
    ActionButton:
        text: 'Profile'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-male-user-50.png')
        on_press: root.dispatch('on_profile_btn_pressed')
    ActionButton:
        text: 'Logout'
        icon: os.path.join(root.base_dir, 'icons', 'icons8-exit-32.png')
        on_press: root.dispatch('on_logout_btn_pressed')
''')


class LoginActionView(ActionView):
    title = StringProperty()

    base_dir = os.path.dirname(__file__)

    def __init__(self, **kwargs):
        super(LoginActionView, self).__init__(**kwargs)

        self.register_event_type('on_triple_tap_action')
        self.register_event_type('on_previous_btn_pressed')
        self.register_event_type('on_exit_btn_pressed')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_triple_tap:
            self.dispatch('on_triple_tap_action')
            return True
        return super(LoginActionView, self).on_touch_down(touch)

    def on_triple_tap_action(ins):
        pass

    def on_previous_btn_pressed(ins):
        pass

    def on_exit_btn_pressed(ins):
        pass


class MainActionView(ActionView):
    SUCCESS_BG_COLOR = (0, 1, 0, 1)
    ERROR_BG_COLOR = (1, 0, 0, 1)
    TEXT_COLOR = (0, 0, 0, 1)

    notification = ObjectProperty()

    title = StringProperty()
    with_previous = BooleanProperty(True)
    text_texture = ObjectProperty()
    num_notifications = NumericProperty(0)

    base_dir = os.path.dirname(__file__)

    def __init__(self, **kwargs):
        super(MainActionView, self).__init__(**kwargs)

        self.circular_bg = None
        self.notification.bind(pos=self.update_drawing, size=self.update_drawing)
        self.get_results_edit()

        self.register_event_type('on_previous_btn_pressed')
        self.register_event_type('on_home_btn_pressed')
        self.register_event_type('on_reports_btn_pressed')
        self.register_event_type('on_settings_btn_pressed')
        self.register_event_type('on_notification_btn_pressed')
        self.register_event_type('on_profile_btn_pressed')
        self.register_event_type('on_logout_btn_pressed')

    def compute_pos(self, instance):
        pos_x = instance.pos[0] + instance.width - 20
        pos_y = instance.pos[1] + (instance.height * .5)
        return (pos_x, pos_y)

    def compute_text_pos(self, pos):
        return (pos[0] + 2.5), (pos[1] + 2.5)

    def on_num_notifications(self, instance, value):
        if value:
            self.draw()
        else:
            self.clear_drawing()

    def draw(self):
        with self.notification.canvas:
            Color(*self.SUCCESS_BG_COLOR)
            pos = self.compute_pos(self.notification)
            self.circular_bg = Ellipse(segments=500, size=(20, 20), pos=pos)
            Color(*self.TEXT_COLOR)
            self.not_text = Ellipse(size=(15, 15), pos=self.compute_text_pos(pos))
            label = CoreLabel(text=str(self.num_notifications))
            label.refresh()
            self.not_text.texture = label.texture

    def clear_drawing(self):
        self.circular_bg.size = (0, 0)
        self.not_text.size = (0, 0)
        self.notification.canvas.ask_update()

    def update_drawing(self, instance, value):
        if self.circular_bg:
            pos = self.compute_pos(instance)
            self.circular_bg.pos = pos
            self.not_text.pos = self.compute_text_pos(pos)

    def get_results_edit(self):
        url = urlTo('results_edit')
        AsyncRequest(url, on_success=self.set_res_switch_state)

    def set_res_switch_state(self, resp):
        state = resp.json()
        switch = self.ids['result_switch']
        switch.active = bool(state)

    def add_notification(self):
        self.num_notifications += 1

    def remove_notification(self):
        self.num_notifications -= 1

    def clear_notification(self):
        self.num_notifications = 0

    def on_previous_btn_pressed(ins):
        pass

    def on_home_btn_pressed(ins):
        pass

    def on_reports_btn_pressed(ins):
        pass

    def on_settings_btn_pressed(ins):
        pass

    def on_notification_btn_pressed(ins):
        pass

    def on_profile_btn_pressed(ins):
        pass

    def on_logout_btn_pressed(ins):
        pass


class MenuBar(ActionBar):
    title = StringProperty()


if __name__ == '__main__':
    from kivy.app import runTouchApp
    root = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    MenuBar:
        id: bar
        size_hint_y: .1
    BoxLayout
            ''')

    main_action_view = MainActionView()
    root.ids['bar'].add_widget(main_action_view)

    runTouchApp(root)
