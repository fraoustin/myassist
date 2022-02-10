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
import urllib

__version__ = "0.0.1"

SEND_SMS = "send sms"


@login_required
def free():
    return render_template('free.html', user=current_user, plugins=current_app.config['PLUGINS'], frees=json.loads(ParamApp.getValue("free")))


@login_required
def del_free():
    frees = json.loads(ParamApp.getValue("free"))
    free = request.form.get('free')
    url = frees[free]
    if request.form.get('free', '') in frees:
        del frees[request.form.get('free', '')]
    paramfree = ParamApp.get("free")
    paramfree.value = json.dumps(frees)
    paramfree.save()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["free"]
            Robot().remove_training(free, "free:%s" % url)
            for answer in conversion['answers']:
                Robot().remove_training("%s %s" % (answer, free), "free:%s" % url)
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("free - del %s" % free)
    return {'status': 'ok'}, 200


@login_required
def add_free():
    frees = json.loads(ParamApp.getValue("free"))
    frees[request.form.get('name')] = request.form.get('token')
    frees[request.form.get('name')] = {'token': request.form.get('token'), 'id': request.form.get('id')}
    paramfree = ParamApp.get("free")
    paramfree.value = json.dumps(frees)
    paramfree.save()
    free = request.form.get('name')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["free"]
            Robot().training(free, "free:%s" % frees[free])
            for answer in conversion['answers']:
                Robot().training("%s %s" % (answer, free), "free:%s" % frees[free])
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("free - add %s" % request.form.get('name'))
    return {'status': 'ok'}, 200


def listenfree(value, response):
    logging.info("free - listen %s" % response)
    if len(response.split('|')) > 2:
        msg = '|'.join(response.split('|')[2:])
        token = response.split('|')[0]
        id = response.split('|')[1]
        speak = False
    else:
        msg = 'sms test from %s' % Robot().name
        token = response.split('|')[0]
        id = response.split('|')[1]
        speak = True
    f = {'user': id, 'pass': token, 'msg': msg}
    url = "https://smsapi.free-mobile.fr/sendmsg?"
    goto = url + urllib.parse.urlencode(f)
    urllib.request.urlopen(goto)
    logging.info("free - send sms %s" % id)
    if speak is True:
        global SEND_SMS
        Robot().emit_event("", "say:%s" % SEND_SMS)


class Free(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/free', 'free', free, methods=['GET'])
        self.add_url_rule('/api/free/del', 'del_free', del_free, methods=['POST'])
        self.add_url_rule('/api/free/add', 'add_free', add_free, methods=['POST'])
        Robot().add_event("free", listenfree)

    def init_db(self):
        if ParamApp.get("free") is None:
            db.session.add(ParamApp(key="free", value=json.dumps({})))
            db.session.commit()
        frees = json.loads(ParamApp.getValue("free"))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']["free"]
                for free in frees.keys():
                    for answer in conversion['answers']:
                        for free in frees:
                            Robot().training("%s %s" % (answer, free), "free:%s|%s" % (frees[free]['token'], frees[free]['id']))
                global SEND_SMS
                SEND_SMS = doc['chatbot']['send']['answers'][0]
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
