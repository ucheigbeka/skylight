from kivy.app import App
from kivy.uix.screenmanager import SlideTransition

from sms import urlTo, get_token, set_details
from sms.forms.signin import SigninWindow
from sms.utils.menubar import LoginActionView
from sms.utils.asyncrequest import AsyncRequest


def logout():
    url = urlTo('logout')
    AsyncRequest(url, method='POST', data={'token': get_token()}, on_success=reset)


def reset(resp=None):
    root = App.get_running_app().root
    sm = root.sm
    root.ids['title_bar_label'].text = 'Student Management System'
    set_details('', '', '', '')
    root.title = ''
    root.is_admin = False
    root.assigned_level = 0

    curr_screen = sm.current_screen
    screens = sm.screens[:]
    for screen in screens:
        if screen == curr_screen or isinstance(screen, SigninWindow):
            continue
        sm.remove_widget(screen)

    for module in root.sm.imported_modules.values():
        if hasattr(module, 'unload') and not hasattr(module, 'SigninWindow'):
            module.unload()

    sm.transition = SlideTransition()
    sm.transition.direction = 'right'
    sm.current = 'signin'
    root.set_menu_view(LoginActionView)
    sm.remove_widget(curr_screen)
    del screens, curr_screen
    sm.forms_dict = {}
