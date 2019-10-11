from kivy.uix.screenmanager import ScreenManager

# Load the forms
from sms.forms.personalinfo import PersonalInfo
from sms.forms.signin import SigninWindow

sm = ScreenManager()

# Adds the screens in the order that they would appear
sm.add_widget(SigninWindow(name='signin'))
sm.add_widget(PersonalInfo(name='personalinfo'))
