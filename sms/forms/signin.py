from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import os

form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'signin.kv')
Builder.load_file(kv_path)


class SigninWindow(Screen):
	form_root = form_root


if __name__ == "__main__":
	from kivy.app import runTouchApp

	runTouchApp(SigninWindow())