from queue import Queue
import threading
import logging
from difflib import SequenceMatcher
import gtts
import time
import tempfile
import os
import random
from num2words import num2words
import speech_recognition as sr
import mpv


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
        del self._logs[5000:]
        if record.levelname != "DEBUG":
            print(self.format(record))


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = RobotHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class Test:
    def __init__(self, value, level=0):
        self.value = value
        self.level = level

    def __lt__(self, other):
        return self.level < other.level

    def __le__(self, other):
        return self.level <= other.level

    def __eq__(self, other):
        return self.level == other.level

    def __ne__(self, other):
        return self.level != other.level

    def __gt__(self, other):
        return self.level > other.level

    def __ge__(self, other):
        return self.level >= other.level


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
        self._langue = "fr-FR"
        self._timeout = 0
        self._energy_threshold = 0
        self._index_mic = 0
        self._direct = "False"

    def run(self):
        self._stop = False
        recognize = sr.Recognizer()
        self.mic = sr.Microphone(device_index=self._index_mic)
        with self.mic as source:
            recognize.adjust_for_ambient_noise(source)
            recognize.dynamic_energy_threshold = True
            self.robot.emit_event("", "say:I am ready")
            while self._stop is False:
                if self.energy_threshold > 0:
                    logging.info("threshold %s" % self.energy_threshold)
                    recognize.energy_threshold = self.energy_threshold
                start = time.time()
                if self.timeout == 0:
                    logging.info("listen without timeout")
                    self.robot.emit_event("", "ledhat:red|red|red")
                    audio = recognize.listen(source)
                else:
                    logging.info("listen with timeout %s" % self._timeout)
                    self.robot.emit_event("", "ledhat:red|red|red")
                    audio = recognize.listen(source, phrase_time_limit=self._timeout)
                end = time.time()
                try:
                    self.robot.emit_event("", "ledhat:green|green|green")
                    logging.info("listen %s second" % str(end-start))
                    data = recognize.recognize_google(audio, language=self.langue)
                    self.robot.emit_event("", "ledhat:blue|blue|blue")
                    logging.info("recognize - %s" % data)
                    self.robot.query(data.strip())
                except Exception:
                    pass

    def stop(self):
        self._stop = True

    @property
    def langue(self):
        return self._langue

    @langue.setter
    def langue(self, value):
        self._langue = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def energy_threshold(self):
        return self._energy_threshold

    @energy_threshold.setter
    def energy_threshold(self, value):
        self._energy_threshold = value


class Robot(metaclass=Singleton):

    def __init__(self, name, level=0.9, andoperator='et'):
        self.name = name
        self._level = level
        self._events = []
        self._responses = []
        self._befores = []
        self._queue = Queue()
        self._thread = None
        self._playbin = None
        self._direct = 'False'
        self.mic = Mic(self)
        self.andoperator = andoperator

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = float(value)

    @logtime
    def training(self, answer, response):
        self._responses.append({"answer": answer.strip(), "response": response.strip()})

    @logtime
    def add_before(self, fct):
        self._befores.append(fct)

    def remove_training(self, answer, response):
        if {"answer": answer, "response": response} in self._responses:
            self._responses.remove({"answer": answer, "response": response})

    def trainings(self, typ):
        return [response for response in self._responses if response['response'].split(":")[0] == typ]

    @property
    def typs_training(self):
        typs = []
        for response in self._responses:
            if response['response'].split(":")[0] not in typs:
                typs.append(response['response'].split(":")[0])
        return typs

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
        if self._thread is None:
            self._thread = QueryThread()
            self._thread.start()
        if len(value) > 0:
            self._queue.put(value.strip())

    @logtime
    def _query(self, values):
        logging.info("querys %s" % values)
        if self.name in values:
            values = values[values.index(self.name)+len(self.name):]
            hasname = True
        else:
            hasname = False
        values = values.split(' %s ' % self.andoperator)
        for value in values:
            try:
                idx = values.index(value) + 1
                if values[idx].split(' ')[0] in [num2words(num, lang=self.mic.langue.split('-')[0]) for num in range(0, 9)] + ['une', ]:
                    values[idx] = value + ' %s ' % self.andoperator + values[idx]
                    values[idx-1] = ''
            except IndexError:
                pass
        logging.info("query list %s" % values)
        for value in [val for val in values if len(val) > 0]:
            logging.info("query treat %s" % value)
            start = time.time()
            if self.direct is False and hasname is False:
                logging.warning("not found name of robot and direct mode desactivate -> break")
                break
            for before in self._befores:
                if len(value) > 0:
                    value = before(value)
                else:
                    continue
            if len(value) > 0:
                value = value.strip()
                logging.info("query %s" % value)
                results = []
                best_match = {"level": 0, "response": []}
                for response in self._responses:
                    results.append(Test(response["response"], similar(value, response["answer"])))
                end = time.time()
                best_match["level"] = max(results).level
                best_match["response"] = [test.value for test in results if best_match["level"] == test.level]
                if best_match["level"] >= self._level:
                    response = random.choice(best_match["response"])
                    logging.debug("_query value: %s  only local base of %s" % (str(end - start), len(self._responses)))
                    self.emit_event(value, response)
                else:
                    response = "notfound"
                    if self.direct is False:
                        logging.debug("_query value: %s  only local base of %s" % (str(end - start), len(self._responses)))
                        self.emit_event(value, response)
                return True
            logging.warning("before cancel %s" % value)
            return False

    def _stopsound(self, *args):
        try:
            self._playbin.stop()
        except Exception:
            pass

    def _playsound(self, url):
        self._playbin = mpv.MPV(ytdl=True)
        self._playbin.play(url)

    @logtime
    def speak(self, words):
        tts = gtts.gTTS(words, lang="fr")
        path = os.path.join(tempfile.gettempdir(), "%s.mp3" % int(time.time()))
        tts.save(path)
        self._playsound(path)

    @property
    def direct(self):
        if self._direct in ('True', 'true'):
            return True
        return False

    @direct.setter
    def direct(self, value):
        self._direct = value
