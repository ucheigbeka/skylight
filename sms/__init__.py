from kivy.uix.screenmanager import ScreenManager

# Load the forms
from sms.forms.personalinfo import PersonalInfo

sm = ScreenManager()

# Adds the screens in the order that they would appear
sm.add_widget(PersonalInfo(name='personalinfo'))
