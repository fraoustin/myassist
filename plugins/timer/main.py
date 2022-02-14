from plugins import Plugin
import logging
from robot import Robot
import os
import threading
import time
import yaml
from num2words import num2words
from db.models import ParamApp

__version__ = "0.0.1"

unitys = {'en': ['hour', 'minute', 'second', 'in'], 'fr': ['heure', 'minute', 'seconde', 'dans']}
TIMER = unitys['en']
NUMBERS = {num2words(elt): elt for elt in range(0, 60)}


class TimerThreadOtherFct(threading.Thread):

    def __init__(self, timer, fct):
        threading.Thread.__init__(self)
        self.robot = Robot()
        self.timer = timer
        self.fct = fct

    def run(self):
        time.sleep(self.timer)
        logging.info("timer other fct - end timer for %s second" % self.timer)
        self.robot.query(self.fct)


def check_timer(value):
    global TIMER
    count = 0
    if ' %s ' % TIMER[3] not in value:
        return value
    search = value.split(' %s ' % TIMER[3])[-1]
    action = ' %s ' % TIMER[3].join(value.split(' %s ' % TIMER[3])[:-1])
    action = action.strip()
    if TIMER[0] not in value and TIMER[1] not in value and TIMER[2] not in value:
        return value
    toseconds = 60 * 60 * 60
    for unity in TIMER[:3]:
        toseconds = toseconds / 60
        if unity in search:
            elt = search.split(unity)[0]
            elt = elt.strip()
            try:
                count = int(elt) * toseconds + count
            except Exception:
                try:
                    print(NUMBERS)
                    print(elt)
                    count = NUMBERS[elt] * toseconds + count
                except Exception:
                    search = ' ' + search
            search = search.split(unity)[1:]
            while len(search) > 0 and search[0] != ' ':
                search = search[1:]
    print("####timer %s" % count)
    if count == 0:
        return value
    logging.info("timer - %s in %s seconds" % (action, count))
    th = TimerThreadOtherFct(count, action)
    th.start()
    return ''


def timerotherfct(value, response):
    th = TimerThreadOtherFct(int(response.split('|')[0]), '|'.join(response.split('|')[1:]))
    th.start()


def buzzer(value, response):
    logging.info("buzzer - %s" % response)
    Robot()._stopsound()
    Robot()._playsound(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "buzzer.mp3"))


class Timer(Plugin):

    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("timer", buzzer)
        Robot().add_before(check_timer)

    def init_db(self):
        lang = ParamApp.getValue("basic_langue")
        global TIMER
        TIMER = unitys[lang]
        global NUMBERS
        NUMBERS = {num2words(elt, lang=lang): elt for elt in range(0, 60)}
        if lang == 'fr':
            numbers_add = {}
            for number in NUMBERS:
                if number[-2:] == 'un':
                    numbers_add[number + 'e'] = NUMBERS[number]
            for number in numbers_add:
                NUMBERS[number] = numbers_add[number]
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']['timer']
                for answer in conversion['answers']:
                    for response in conversion['responses']:
                        Robot().training(answer, response)
            except yaml.YAMLError as exc:
                print(exc)
