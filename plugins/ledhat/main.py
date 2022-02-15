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
        self._pixels = ['black', 'black', 'black']
    
    def set_pixel(self, pixel, color):
        if pixel == 'all':
            for pixel in range(3):
                self._pixels[pixel] = color
        else:
            self._pixels[pixel] = color
        for pixel in range(3):
            self._dev.set_pixel(pixel, *COLORS[self._pixels[pixel]])
        self._dev.show()
    
    def clear(self):
        for pixel in range(3):
            self.set_pixel(pixel, 'black')


def ledhat(value, response):
    LedHatManage().set_pixel(*response.split("|"))


class Ledhat(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("ledhat", ledhat)
        LedHatManage().clear()
        for color in COLORS:
            LedHatManage().set_pixel('all', color)
            time.sleep(2)
        LedHatManage().clear()

