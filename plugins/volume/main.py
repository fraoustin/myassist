from plugins import Plugin
from robot import Robot
import os
import yaml
from db import db
from db.models import ParamApp
import math

__version__ = "0.0.1"

CHANNELS = []
BASIC_VOLUME = math.fabs(50)
VAL2VOL = ""
VOL2VAL = ""


def get_volume():
    global CHANNELS
    global VAL2VOL
    stream = os.popen('amixer get %s' % CHANNELS[0])
    output = stream.read()
    value = 0
    for extract in output.split('['):
        extract = extract.split('%]')[0]
        try:
            value = int(extract)
        except Exception:
            pass
    return int(eval(VAL2VOL.replace('value', str(value))))


def set_volume(volume):
    global CHANNELS
    global VOL2VAL
    value = int(eval(VOL2VAL.replace("volume", str(volume))))
    for channel in CHANNELS:
        os.system("amixer set %s %s%%" % (channel, value))


def volume_up(value, response):
    vol = get_volume()
    if vol == 0:
        new_vol = BASIC_VOLUME
    else:
        new_vol = vol + 10
        if new_vol > 100:
            new_vol = 100
    set_volume(new_vol)


def volume_down(value, response):
    vol = get_volume()
    new_vol = vol - 10
    if new_vol < 0:
        new_vol = 0
    set_volume(new_vol)


def volume_mute(value, response):
    set_volume(0)


class Volume(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                for key in doc['chatbot']:
                    conversion = doc['chatbot'][key]
                    for answer in conversion['answers']:
                        for response in conversion['responses']:
                            Robot().training(answer, response)
            except yaml.YAMLError as exc:
                print(exc)
        Robot().add_event("volume_up", volume_up)
        Robot().add_event("volume_down", volume_down)
        Robot().add_event("volume_mute", volume_mute)

    def init_db(self):
        if ParamApp.get("basic_volume") is None:
            db.session.add(ParamApp(key="basic_volume", value="60"))
            db.session.commit()
        if ParamApp.get("basic_volume channels") is None:
            db.session.add(ParamApp(key="basic_volume channels", value="Speaker"))
            db.session.commit()
        if ParamApp.get("basic_volume val2vol") is None:
            db.session.add(ParamApp(key="basic_volume val2vol", value="20.189*math.log(value)+7.0618"))
            db.session.commit()
        if ParamApp.get("basic_volume vol2val") is None:
            db.session.add(ParamApp(key="basic_volume vol2val", value="0.7059*math.exp(0.0495*volume)"))
            db.session.commit()
        global VAL2VOL
        VAL2VOL = ParamApp.getValue("basic_volume val2vol")
        global VOL2VAL
        VAL2VOL = ParamApp.getValue("basic_volume vol2val")
        global CHANNELS
        CHANNELS = ParamApp.getValue("basic_volume channels").split(";")
        global BASIC_VOLUME
        BASIC_VOLUME = int(ParamApp.getValue("basic_volume"))
        set_volume(int(ParamApp.getValue("basic_volume")))
