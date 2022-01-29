from plugins import Plugin
from robot import Robot
import gtts
from playsound import playsound
import time
import tempfile
import os


def tovoice(value, response):
    with tempfile.TemporaryDirectory() as tmpdirname:
        tts = gtts.gTTS(response, lang="fr")
        path = os.path.join(tmpdirname, "%s.mp3" % int(time.time()))
        tts.save(path)
        playsound(path)


class Tovoice(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("say", tovoice)
