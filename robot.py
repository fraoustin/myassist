from queue import Queue
import threading
import logging
from difflib import SequenceMatcher
import gtts
import time
import tempfile
import os
import random
from os.path import abspath, exists
from urllib.request import pathname2url
import speech_recognition as sr
from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')


class RobotHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        self._logs = []

    def clear(self):
        del self._logs[:]

    @property
    def logs(self):
        return self._logs

    def emit(self, record):
        self._logs.insert(0, record)
        del self._logs[500:]


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = RobotHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


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


def logtime(func):
    def decorateur(*args, **kwargs):
        start = time.time()
        resultat = func(*args, **kwargs)
        end = time.time()
        logging.debug("treatment %s : %s  with param %s %s" % (func.__name__, end - start, str(args), str(kwargs)))
        return resultat
    return decorateur


class Mic(threading.Thread):

    def __init__(self, robot):
        threading.Thread.__init__(self)
        self.robot = robot
        self.langue = "fr-FR"
        self._index_mic = 0

    def run(self):
        self._stop = False
        recognize = sr.Recognizer()
        mic = sr.Microphone(device_index=self._index_mic)
        with mic as source:
            recognize.adjust_for_ambient_noise(source)
            while self._stop is False:
                audio = recognize.listen(source)
                try:
                    data = recognize.recognize_google(audio, language=self.langue)
                    print(data)
                    if self.robot.name in data:
                        data = data[data.index(self.robot.name)+len(self.robot.name):]
                    self.robot.query(data.upper())
                except Exception:
                    pass

    def stop(self):
        self._stop = False

    @property
    def index_mic(self):
        return self._index_mic

    @index_mic.setter
    def index_mic(self, value):
        self.stop()
        self._index_mic = value
        self.start()


class Robot(metaclass=Singleton):

    def __init__(self, name, level=0.9):
        self.name = name
        self._level = level
        self._events = []
        self._responses = []
        self._queue = Queue()
        self._thread = None
        self._playbin = None
        self.mic = Mic(self)
        Gst.init(None)

    @logtime
    def training(self, answer, response):
        self._responses.append({"answer": answer.upper(), "response": response})

    def remove_training(self, answer, response):
        if {"answer": answer, "response": response} in self._responses:
            self._responses.remove({"answer": answer, "response": response})

    @logtime
    def add_event(self, name, obs):
        if name not in [event.name for event in self._events]:
            self._events.append(Event(name))
        [event for event in self._events if event.name == name][0] += obs

    @logtime
    def emit_event(self, value, response):
        if response.split(":")[0] in [event.name for event in self._events]:
            logging.info("robot - emit %s" % response)
            [event for event in self._events if event.name == response.split(":")[0]][0](value, ":".join(response.split(":")[1:]))

    def query(self, value):
        if len(value) > 0:
            self._queue.put(value)
        if self._thread is None:
            self._thread = QueryThread()
            self._thread.start()

    @logtime
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
            print(value, best_match["level"], best_match["response"][0])
            response = "notfound"
        self.emit_event(value, response)

    def _stopsound(self, *args):
        try:
            self._playbin.set_state(Gst.State.READY)
        except Exception:
            pass

    @logtime
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

    @logtime
    def speak(self, words):
        with tempfile.TemporaryDirectory() as tmpdirname:
            tts = gtts.gTTS(words, lang="fr")
            path = os.path.join(tmpdirname, "%s.mp3" % int(time.time()))
            tts.save(path)
            self._playsound(path)
