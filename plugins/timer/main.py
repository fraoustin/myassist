from plugins import Plugin
import logging
from robot import Robot
import os
import threading
import time
import yaml
from num2words import num2words
from db import db
from db.models import ParamApp

__version__ = "0.0.1"

unitys = {'en':['hour', 'minute'], 'fr':['heure', 'minute']}

RESPONSE_TIMER = "timer load for"
END_TIMER = "end timer"
MINUTE_TIMER = "minute"


class TimerThread(threading.Thread):

    def __init__(self, timer):
        threading.Thread.__init__(self)
        self.robot = Robot()
        self.timer = timer * 60

    def run(self):
        global END_TIMER
        time.sleep(self.timer)
        logging.info("timer - end timer for %s second" % self.timer)
        self.robot.emit_event("", "say:%s" % END_TIMER)
        self.robot._stopsound()
        self.robot._playsound(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "timer.mp3"))


class TimerSleepThread(threading.Thread):

    def __init__(self, timer):
        threading.Thread.__init__(self)
        self.robot = Robot()
        self.timer = timer * 60

    def run(self):
        global END_TIMER
        time.sleep(self.timer)
        logging.info("timer - end timer sleep for %s second" % self.timer)
        self.robot.emit_event("", "volume_mute")


def timer(value, response):
    global RESPONSE_TIMER
    global MINUTE_TIMER
    logging.info("timer - run timer for %s second" % response)
    th = TimerThread(int(response))
    th.start()
    Robot().emit_event("", "say:%s %s %s" % (RESPONSE_TIMER, response, MINUTE_TIMER))

def sleep(value, response):
    global RESPONSE_TIMER
    global MINUTE_TIMER
    logging.info("timer - run timer sleep for %s second" % response)
    th = TimerSleepThread(int(response))
    th.start()
    Robot().emit_event("", "say:%s %s %s" % (RESPONSE_TIMER, response, MINUTE_TIMER))


class Timer(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("timer", timer)
        Robot().add_event("sleep", sleep)
    
    def init_db(self):
        lang = ParamApp.getValue("basic_langue")
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']['timer']
                for answer in conversion['answers']:
                    for response in conversion['responses']:
                        Robot().training(answer, response)
                        for number in range(1, 60):
                            Robot().training(answer + " " + num2words(number, lang=lang) + " " + unitys[lang][0], "%s:%s" % (response, 60*number))
                            Robot().training(answer + " " + num2words(number, lang=lang) + " " + unitys[lang][1], "%s:%s" % (response, number))
                        for numberh in range(1, 8):
                            for numberm in range(1, 60):
                                Robot().training(answer + " " + num2words(numberh, lang=lang) + " " + unitys[lang][0] + " " + num2words(numberm, lang=lang) + " " + unitys[lang][1], "%s:%s" % (response, 60*numberh+numberm))
                                Robot().training(answer + " " + str(numberh) + " " + unitys[lang][0] + " " + str(numberm) + " " + unitys[lang][1], "%s:%s" % (response, 60*numberh+numberm))
                                Robot().training(answer + " " + num2words(numberh, lang=lang) + " " + unitys[lang][0] + " " + num2words(numberm, lang=lang), "%s:%s" % (response, 60*numberh+numberm))
                                Robot().training(answer + " " + str(numberh) + " " + unitys[lang][0] + " " + str(numberm), "%s:%s" % (response, 60*numberh+numberm))
                                Robot().training(answer + " " + str(numberh) + " " + str(numberm), "%s:%s" % (response, 60*numberh+numberm))
                conversion = doc['chatbot']['sleep']
                for answer in conversion['answers']:
                    for response in conversion['responses']:
                        for number in range(1, 99):
                            Robot().training(answer + " " + num2words(number, lang=lang) + " " + unitys[lang][1], "%s:%s" % (response, number))
                global RESPONSE_TIMER
                RESPONSE_TIMER = doc['chatbot']['response']['responses'][0]
                global END_TIMER
                END_TIMER = doc['chatbot']['end']['responses'][0]
                global MINUTE_TIMER
                MINUTE_TIMER = unitys[lang][1]
            except yaml.YAMLError as exc:
                print(exc)
