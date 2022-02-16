from plugins import Plugin
import time
from robot import Robot, Singleton
from plugins.ledhat import apa102

__version__ = "0.0.1"

COLORS = {"red": (48, 0, 0),
    'green': (0, 48, 0),
    'blue': (0, 0, 48),
    'yellow': (48, 48, 0),
    'indiglo': (0, 48, 48),
    'purple': (48, 0, 48),
    'black': (0, 0, 0),
    'white': (48, 48, 48)}


class LedHatManage(metaclass=Singleton):

    def __init__(self):
        self._dev = apa102.APA102(num_led=3)
        self.clear()

    def set_pixel(self, *pixels):
        id = 0
        for pixel in pixels:
            if pixel in COLORS:
                self._dev.set_pixel(id, *COLORS[pixel])
        self._dev.show()

    def clear(self):
        self.set_pixel('black', 'black', 'black')


def ledhat(value, response):
    LedHatManage().set_pixel(*response.split("|"))


class Ledhat(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("ledhat", ledhat)
        LedHatManage().clear()
        for color in COLORS:
            LedHatManage().set_pixel(color, color, color)
            time.sleep(2)
        LedHatManage().clear()
