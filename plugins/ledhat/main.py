from plugins import Plugin
import time
from robot import Robot, Singleton
from plugins.ledhat import apa102
import threading

__version__ = "0.0.1"

COLORS = {"redl": (12, 0, 0),
    "red": (48, 0, 0),
    "redh": (96, 0, 0),
    'greenl': (0, 12, 0),
    'green': (0, 48, 0),
    'greenh': (0, 96, 0),
    'bluel': (0, 0, 12),
    'blue': (0, 0, 48),
    'blueh': (0, 0, 96),
    'yellowl': (12, 12, 0),
    'yellow': (48, 48, 0),
    'yellowh': (96, 96, 0),
    'indiglol': (0, 12, 12),
    'indiglo': (0, 48, 48),
    'indigloh': (0, 96, 96),
    'purplel': (12, 0, 12),
    'purple': (48, 0, 48),
    'purpleh': (96, 0, 96),
    'whitel': (12, 12, 12),
    'white': (48, 48, 48),
    'whiteh': (96, 96, 96),
    'black': (0, 0, 0)}


class LedHatManage(metaclass=Singleton):

    def __init__(self):
        self._dev = apa102.APA102(num_led=3)
        self.clear()

    def set_pixel(self, *pixels):
        id = 0
        for pixel in pixels:
            if pixel in COLORS:
                self._dev.set_pixel(id, *COLORS[pixel])
            id = id + 1
        self._dev.show()

    def clear(self):
        self.set_pixel('black', 'black', 'black')


def ledhat(value, response):
    LedHatManage().set_pixel(*response.split("|"))


def test():
    LedHatManage().clear()
    for color in COLORS:
        LedHatManage().set_pixel(color, color, color)
        time.sleep(1)
    LedHatManage().clear()


class Ledhat(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("ledhat", ledhat)
        th = threading.Thread(target=test)
        th.start()
