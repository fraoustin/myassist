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

__version__ = "0.0.1"


@login_required
def radio():
    return render_template('radio.html', user=current_user, plugins=current_app.config['PLUGINS'], radios=json.loads(ParamApp.getValue("radio")))


@login_required
def del_radio():
    radios = json.loads(ParamApp.getValue("radio"))
    radio = request.form.get('radio')
    url = radios[radio]
    if request.form.get('radio', '') in radios:
        del radios[request.form.get('radio', '')]
    paramradio = ParamApp.get("radio")
    paramradio.value = json.dumps(radios)
    paramradio.save()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["radio"]
            Robot().remove_training(radio, "radio:%s" % url)
            for answer in conversion['answers']:
                Robot().remove_training("%s %s" % (answer, radio), "radio:%s" % url)
            for answer in conversion['stop']:
                Robot().remove_training("%s %s" % (answer, radio), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("radio - del %s" % radio)
    return {'status': 'ok'}, 200


@login_required
def add_radio():
    radios = json.loads(ParamApp.getValue("radio"))
    radios[request.form.get('name')] = request.form.get('url')
    paramradio = ParamApp.get("radio")
    paramradio.value = json.dumps(radios)
    paramradio.save()
    radio = request.form.get('name')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["radio"]
            Robot().training(radio, "radio:%s" % radios[radio])
            for answer in conversion['answers']:
                Robot().training("%s %s" % (answer, radio), "radio:%s" % radios[radio])
            for answer in conversion['stop']:
                Robot().training("%s %s" % (answer, radio), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("radio - add %s" % request.form.get('name'))
    return {'status': 'ok'}, 200


def listenradio(value, response):
    logging.info("radio - listen %s" % response)
    Robot()._stopsound()
    Robot()._playsound(response)


def stop(value, response):
    Robot()._stopsound()


class Radio(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/radio', 'radio', radio, methods=['GET'])
        self.add_url_rule('/api/radio/del', 'del_radio', del_radio, methods=['POST'])
        self.add_url_rule('/api/radio/add', 'add_radio', add_radio, methods=['POST'])
        Robot().add_event("radio", listenradio)
        Robot().add_event("stop", stop)

    def init_db(self):
        if ParamApp.get("radio") is None:
            value = {
                'franceinter': 'https://icecast.radiofrance.fr/franceinter-midfi.mp3?id=radiofrance',
                'tsfjazz': 'https://tsfjazz.ice.infomaniak.ch:80/tsfjazz-high.mp3',
                'franceinfo': 'http://direct.franceinfo.fr/live/franceinfo-midfi.mp3',
                'fip': 'https://icecast.radiofrance.fr/fip-midfi.mp3?id=fip'
            }
            db.session.add(ParamApp(key="radio", value=json.dumps(value)))
            db.session.commit()
        radios = json.loads(ParamApp.getValue("radio"))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']["radio"]
                for radio in radios.keys():
                    Robot().training(radio, "radio:%s" % radios[radio])
                    for answer in conversion['answers']:
                        Robot().training("%s %s" % (answer, radio), "radio:%s" % radios[radio])
                for radio in radios.keys():
                    for answer in conversion['stop']:
                        Robot().training("%s %s" % (answer, radio), "stop")
                for answer in conversion['stop']:
                    Robot().training(answer, "stop")
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
