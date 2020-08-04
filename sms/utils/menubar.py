from kivy.lang import Builder
from kivy.uix.actionbar import ActionBar
from kivy.properties import StringProperty

Builder.load_string('''
<Separator@Label+ActionItem>:
    size_hint_x: .7

<MenuBar>:
    ActionView:
        spacing: dp(20)
        ActionPrevious:
            title: root.title
        ActionButton:
            text: 'Reports'
            icon: "icons/icons8-business-report-32.png"
            important: True
        ActionButton:
            text: 'Home'
            icon: "icons/icons8-home-32.png"
            text: 'home'
            important: True
        ActionButton:
            text: 'Settings'
            icon: "icons/icons8-settings-32.png"
            important: True
        Separator:
            important: True
        ActionButton:
            text: 'Notifications'
            icon: "icons/icons8-bell-32.png"
        ActionButton:
            text: 'Profile'
            icon: "icons/icons8-male-user-50.png"
        ActionButton:
            text: 'Logout'
            icon: "icons/icons8-exit-32.png"
''')


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
    BoxLayout
            ''')
    )
