from queue import Queue
import threading
from difflib import SequenceMatcher
import gtts
import time
import tempfile
import os
import random
from os.path import abspath, exists
from urllib.request import pathname2url
from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class PlaysoundException(Exception):
    pass


class QueryThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.robot = Robot()

    def run(self):
        while True:
            self.robot._query(self.robot._queue.get())


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Event(object):
    def __init__(self, name):
        self.name = name
        self._obss = []

    def __iadd__(self, obs):
        if not callable(obs):
            raise TypeError("%s is not callable" % str(obs))
        obss = self._obss
        if obs not in obss:
            obss.append(obs)
        return self

    def __isub__(self, obs):
        """ retire un obs """
        obss = self._obss
        if obs in obss:
            obss.remove(obs)
        return self

    def __call__(self, *args, **kw):
        [obs(*args, **kw) for obs in self._obss]


class Robot(metaclass=Singleton):

    def __init__(self, name, level=0.9):
        self._level = level
        self._events = []
        self._responses = []
        self._queue = Queue()
        self._thread = None
        self._playbin = None
        Gst.init(None)

    def training(self, answer, response):
        self._responses.append({"answer": answer, "response": response})

    def remove_training(self, answer, response):
        if {"answer": answer, "response": response} in self._responses:
            self._responses.remove({"answer": answer, "response": response})

    def add_event(self, name, obs):
        if name not in [event.name for event in self._events]:
            self._events.append(Event(name))
        [event for event in self._events if event.name == name][0] += obs

    def emit_event(self, value, response):
        if response.split(":")[0] in [event.name for event in self._events]:
            [event for event in self._events if event.name == response.split(":")[0]][0](value, ":".join(response.split(":")[1:]))

    def query(self, value):
        if len(value) > 0:
            self._queue.put(value)
        if self._thread is None:
            self._thread = QueryThread()
            self._thread.start()

    def _query(self, value):
        best_match = {"level": 0, "response": []}
        for response in self._responses:
            test = similar(value, response["answer"])
            if test > best_match["level"]:
                best_match = {"level": test, "response": [response["response"], ]}
            if test == best_match["level"]:
                best_match["response"].append(response["response"])
        if best_match["level"] >= self._level:
            response = random.choice(best_match["response"])
        else:
            response = "notfound"
        self.emit_event(value, response)

    def _stopsound(self, *args):
        try:
            self._playbin.set_state(Gst.State.READY)
        except Exception:
            pass

    def _playsound(self, url):
        self._playbin = Gst.ElementFactory.make('playbin', 'playbin')
        if url.startswith(('http://', 'https://')):
            self._playbin.props.uri = url
        else:
            path = abspath(url)
            if not exists(path):
                raise PlaysoundException(u'File not found: {}'.format(path))
            self._playbin.props.uri = 'file://' + pathname2url(path)
        self._playbin.set_state(Gst.State.PLAYING)

    def speak(self, words):
        with tempfile.TemporaryDirectory() as tmpdirname:
            tts = gtts.gTTS(words, lang="fr")
            path = os.path.join(tmpdirname, "%s.mp3" % int(time.time()))
            tts.save(path)
            self._playsound(path)
