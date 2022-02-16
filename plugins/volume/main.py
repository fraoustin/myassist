from plugins import Plugin
from robot import Robot
import os
import yaml
from pulsectl import Pulse, PulseVolumeInfo
from db import db
from db.models import ParamApp

__version__ = "0.0.1"


def get_volume():
    with Pulse() as pulse:
        sink = pulse.sink_list()[0]
        return sink.volume.value_flat


def set_volume(value):
    with Pulse() as pulse:
        sink = pulse.sink_list()[0]
        n_channels = len(sink.volume.values)
        new_volume = PulseVolumeInfo(0.9, n_channels)
        pulse.volume_set(sink, new_volume)


def volume_up(value, response):
    vol = get_volume()
    if vol == 0:
        new_vol = float(ParamApp.getValue("basic_volume"))
    else:
        new_vol = vol + 0.1
        if new_vol > 1:
            new_vol = 1
    set_volume(new_vol)


def volume_down(value, response):
    vol = get_volume()
    new_vol = vol - 0.1
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
            db.session.add(ParamApp(key="basic_volume", value="0.5"))
            db.session.commit()
        set_volume(float(ParamApp.getValue("basic_volume")))
