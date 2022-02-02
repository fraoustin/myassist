from plugins import Plugin
from robot import Robot
from db import db
from db.models import ParamApp
import json
import os
import yaml
from flask import current_app, render_template, request
from flask_login import login_required, current_user

__version__ = "0.0.1"


@login_required
def timing():
    return render_template('timing.html', user=current_user, plugins=current_app.config['PLUGINS'], timings=json.loads(ParamApp.getValue("timing")))


@login_required
def del_timing():
    timings = json.loads(ParamApp.getValue("timing"))
    timingdel = request.form.get('timing')
    print(timingdel)
    timings = [ tim for tim in timings if tim["name"] != timingdel]
    print(timing)
    paramtiming = ParamApp.get("timing")
    paramtiming.value = json.dumps(timings)
    paramtiming.save()
    return {'status': 'ok'}, 200


@login_required
def add_timing():
    timings = json.loads(ParamApp.getValue("timing"))
    timings.append(json.loads(request.form.get('timing')))
    paramtiming = ParamApp.get("timing")
    paramtiming.value = json.dumps(timings)
    paramtiming.save()
    return {'status': 'ok'}, 200


def listentiming(value, response):
    Robot()._stopsound()
    Robot()._playsound(response)


def stop(value, response):
    Robot()._stopsound()


class Timing(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/timing', 'timing', timing, methods=['GET'])
        self.add_url_rule('/api/timing/del', 'del_timing', del_timing, methods=['POST'])
        self.add_url_rule('/api/timing/add', 'add_timing', add_timing, methods=['POST'])
        Robot().add_event("timing", listentiming)
        Robot().add_event("stop", stop)

    def init_db(self):
        if ParamApp.get("timing") is None:
            db.session.add(ParamApp(key="timing", value=json.dumps([])))
            db.session.commit()
