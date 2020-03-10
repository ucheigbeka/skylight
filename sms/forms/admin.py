import os
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen


form_root = os.path.dirname(__file__)
kv_path = os.path.join(form_root, 'kv_container', 'admin.kv')
Builder.load_file(kv_path)




class Administrator(Screen):
	form_root = form_root

	def __init__(self, **kwargs):
		super(Administrator, self).__init__(**kwargs)



if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.core.window import Window

    Window.maximize()
    runTouchApp(Administrator())
