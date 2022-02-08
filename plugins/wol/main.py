from plugins import Plugin
import logging
from robot import Robot
from db import db
from db.models import ParamApp
import json
import os
import yaml
from flask import current_app, render_template, request
from flask_login import login_required, current_user
from wakeonlan import send_magic_packet

__version__ = "0.0.1"

START_COMPUTER = "run computer"


@login_required
def wol():
    return render_template('wol.html', user=current_user, plugins=current_app.config['PLUGINS'], wols=json.loads(ParamApp.getValue("wol")))


@login_required
def del_wol():
    wols = json.loads(ParamApp.getValue("wol"))
    wol = request.form.get('wol')
    url = wols[wol]
    if request.form.get('wol', '') in wols:
        del wols[request.form.get('wol', '')]
    paramwol = ParamApp.get("wol")
    paramwol.value = json.dumps(wols)
    paramwol.save()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["wol"]
            Robot().remove_training(wol, "wol:%s" % url)
            for answer in conversion['answers']:
                Robot().remove_training("%s %s" % (answer, wol), "wol:%s" % url)
            for answer in conversion['stop']:
                Robot().remove_training("%s %s" % (answer, wol), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("wol - del %s" % wol)
    return {'status': 'ok'}, 200


@login_required
def add_wol():
    wols = json.loads(ParamApp.getValue("wol"))
    wols[request.form.get('name')] = request.form.get('url')
    paramwol = ParamApp.get("wol")
    paramwol.value = json.dumps(wols)
    paramwol.save()
    wol = request.form.get('name')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["wol"]
            Robot().training(wol, "wol:%s" % wols[wol])
            for answer in conversion['answers']:
                Robot().training("%s %s" % (answer, wol), "wol:%s" % wols[wol])
            for answer in conversion['stop']:
                Robot().training("%s %s" % (answer, wol), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("wol - add %s" % request.form.get('name'))
    return {'status': 'ok'}, 200


def listenwol(value, response):
    global START_COMPUTER
    logging.info("wol - listen %s" % response)
    send_magic_packet(response)
    Robot().emit_event("", "say:%s" % START_COMPUTER)


class Wol(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/wol', 'wol', wol, methods=['GET'])
        self.add_url_rule('/api/wol/del', 'del_wol', del_wol, methods=['POST'])
        self.add_url_rule('/api/wol/add', 'add_wol', add_wol, methods=['POST'])
        Robot().add_event("wol", listenwol)

    def init_db(self):
        if ParamApp.get("wol") is None:
            db.session.add(ParamApp(key="wol", value=json.dumps({})))
            db.session.commit()
        wols = json.loads(ParamApp.getValue("wol"))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']["wol"]
                for wol in wols.keys():
                    Robot().training(wol, "wol:%s" % wols[wol])
                    for answer in conversion['answers']:
                        Robot().training("%s %s" % (answer, wol), "wol:%s" % wols[wol])
                for wol in wols.keys():
                    for answer in conversion['stop']:
                        Robot().training("%s %s" % (answer, wol), "stop")
                for answer in conversion['stop']:
                    Robot().training(answer, "stop")
                global START_COMPUTER
                START_COMPUTER = doc['chatbot']['start']['answers'][0]
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
