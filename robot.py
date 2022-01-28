from queue import Queue
import threading
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer


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


class Robot(ChatBot, metaclass=Singleton):

    def __init__(self, *args, **kw):
        ChatBot.__init__(self, *args, **kw)
        self._trainer = ListTrainer(self)
        self._events = []
        self._queue = Queue()
        self._thread = None

    def training(self, answer, response):
        self._trainer.train([answer, response])

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
        response = str(self.get_response(value))
        self.emit_event(value, response)
