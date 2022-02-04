from plugins import Plugin
from robot import Robot, Singleton
from db import db
from db.models import ParamApp
import json
import threading
import logging
import os
import time
import yaml
from flask import current_app, render_template, request
from flask_login import login_required, current_user
import schedule

__version__ = "0.0.1"


class TimingThread(threading.Thread, metaclass=Singleton):

    def __init__(self):
        threading.Thread.__init__(self)
        self.robot = Robot()
        self._scheduler = schedule.Scheduler()
        self.stop = False
        self._weekdays = {
            "monday": self._scheduler.every().monday,
            "tuesday": self._scheduler.every().tuesday,
            "wednesday": self._scheduler.every().wednesday,
            "thursday": self._scheduler.every().thursday,
            "friday": self._scheduler.every().friday,
            "saturday": self._scheduler.every().saturday,
            "sunday": self._scheduler.every().sunday,
        }

    def run(self):
        logging.info("timing - run schedule")
        while self.stop is False:
            self._scheduler.run_pending()
            time.sleep(1)
    
    def clear(self):
        logging.info("timing - clear schedule")
        self._scheduler.clear()
    
    def add_job(self, day, timer, job):
        self._weekdays[day].at(timer).do(job)


@login_required
def timing():
    return render_template('timing.html', user=current_user, plugins=current_app.config['PLUGINS'], timings=json.loads(ParamApp.getValue("timing")), json=json)


@login_required
def del_timing():
    timings = json.loads(ParamApp.getValue("timing"))
    timingdel = request.form.get('timing')
    timings = [ tim for tim in timings if tim["name"] != timingdel]
    paramtiming = ParamApp.get("timing")
    paramtiming.value = json.dumps(timings)
    paramtiming.save()
    settiming(timings)
    logging.info("timing - del %s" % timingdel)
    return {'status': 'ok'}, 200


@login_required
def add_timing():
    timings = json.loads(ParamApp.getValue("timing"))
    name = json.loads(request.form.get('timing'))["oldname"]
    timings = [ tim for tim in timings if tim["name"] != name]
    timings.append(json.loads(request.form.get('timing')))
    paramtiming = ParamApp.get("timing")
    paramtiming.value = json.dumps(timings)
    paramtiming.save()
    settiming(timings)
    logging.info("timing - add %s" % name)
    return {'status': 'ok'}, 200


def fcttiming(steps):
    def fct():
        for step in steps:
            logging.info("timing - emit %s" % step)
            Robot().emit_event("", step)
            time.sleep(1)
    return fct

def settiming(params):
    TimingThread().clear()
    for param in params:
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            if param[day] == True:
                logging.debug("timing - add schedule %s %s:%s %s" % (day, param['hour'], param['minute'], param['steps']))
                TimingThread().add_job(day, "%s:%s" % (param['hour'], param['minute']), fcttiming(param['steps']))


class Timing(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/timing', 'timing', timing, methods=['GET'])
        self.add_url_rule('/api/timing/del', 'del_timing', del_timing, methods=['POST'])
        self.add_url_rule('/api/timing/add', 'add_timing', add_timing, methods=['POST'])

    def init_db(self):
        if ParamApp.get("timing") is None:
            db.session.add(ParamApp(key="timing", value=json.dumps([])))
            db.session.commit()
        settiming(json.loads(ParamApp.getValue("timing")))
        TimingThread().start()
