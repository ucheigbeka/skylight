from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage

from sms.utils.menubutton import MenuButton


class ImageButton(ButtonBehavior, AsyncImage):
    pass


class ImageButtonWithBackground(ImageButton, MenuButton):
    pass
