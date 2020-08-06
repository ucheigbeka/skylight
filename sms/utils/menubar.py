import os
from kivy.lang import Builder
from kivy.uix.actionbar import ActionBar, ActionView
from kivy.properties import StringProperty, BooleanProperty

Builder.load_string('''
#:import os os

<Separator@Label+ActionItem>:
    size_hint_x: .7

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
    ActionButton:
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

        self.register_event_type('on_previous_btn_pressed')
        self.register_event_type('on_exit_btn_pressed')

    def on_previous_btn_pressed(ins):
        pass

    def on_exit_btn_pressed(ins):
        pass


class MainActionView(ActionView):
    title = StringProperty()
    with_previous = BooleanProperty(True)

    base_dir = os.path.dirname(__file__)

    def __init__(self, **kwargs):
        super(MainActionView, self).__init__(**kwargs)

        self.register_event_type('on_previous_btn_pressed')
        self.register_event_type('on_home_btn_pressed')
        self.register_event_type('on_reports_btn_pressed')
        self.register_event_type('on_settings_btn_pressed')
        self.register_event_type('on_notification_btn_pressed')
        self.register_event_type('on_profile_btn_pressed')
        self.register_event_type('on_logout_btn_pressed')

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

    runTouchApp(
        Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    MenuBar:
        size_hint_y: .1
        LoginActionView
    BoxLayout
            ''')
    )
