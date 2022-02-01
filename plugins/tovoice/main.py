from plugins import Plugin
from robot import Robot

__version__ = "0.0.1"


def tovoice(value, response):
    if len(response) > 0:
        Robot().speak(response)


class Tovoice(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("say", tovoice)
