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
def alarm():
    return render_template('alarm.html', user=current_user, plugins=current_app.config['PLUGINS'], alarms=json.loads(ParamApp.getValue("alarm")))


@login_required
def del_alarm():
    alarms = json.loads(ParamApp.getValue("alarm"))
    alarm = request.form.get('alarm')
    url = alarms[alarm]
    if request.form.get('alarm', '') in alarms:
        del alarms[request.form.get('alarm', '')]
    paramalarm = ParamApp.get("alarm")
    paramalarm.value = json.dumps(alarms)
    paramalarm.save()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["alarm"]
            Robot().remove_training(alarm, "alarm:%s" % url)
            for answer in conversion['answers']:
                Robot().remove_training("%s %s" % (answer, alarm), "alarm:%s" % url)
            for answer in conversion['stop']:
                Robot().remove_training("%s %s" % (answer, alarm), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    return {'status': 'ok'}, 200


@login_required
def add_alarm():
    alarms = json.loads(ParamApp.getValue("alarm"))
    alarms[request.form.get('name')] = request.form.get('url')
    paramalarm = ParamApp.get("alarm")
    paramalarm.value = json.dumps(alarms)
    paramalarm.save()
    alarm = request.form.get('name')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["alarm"]
            Robot().training(alarm, "alarm:%s" % alarms[alarm])
            for answer in conversion['answers']:
                Robot().training("%s %s" % (answer, alarm), "alarm:%s" % alarms[alarm])
            for answer in conversion['stop']:
                Robot().training("%s %s" % (answer, alarm), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    return {'status': 'ok'}, 200


def listenalarm(value, response):
    Robot()._stopsound()
    Robot()._playsound(response)


def stop(value, response):
    Robot()._stopsound()


class Alarm(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/alarm', 'alarm', alarm, methods=['GET'])
        self.add_url_rule('/api/alarm/del', 'del_alarm', del_alarm, methods=['POST'])
        self.add_url_rule('/api/alarm/add', 'add_alarm', add_alarm, methods=['POST'])
        Robot().add_event("alarm", listenalarm)
        Robot().add_event("stop", stop)

    def init_db(self):
        if ParamApp.get("alarm") is None:
            db.session.add(ParamApp(key="alarm", value=json.dumps({})))
            db.session.commit()
