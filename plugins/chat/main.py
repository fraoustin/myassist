import os
import time
from flask import current_app, render_template, request
from flask_login import login_required, current_user
from plugins import Plugin
from robot import Robot
import yaml
import logging

__version__ = "0.0.1"

HISTORIC_SAYS = []


@login_required
def chat():
    return render_template('chat.html', user=current_user, plugins=current_app.config['PLUGINS'])


@login_required
def query():
    query = request.form.get('query', '')
    Robot().query(query)
    return {'status': 'ok'}, 200


@login_required
def historic():
    return {"responses": HISTORIC_SAYS}, 200


def saychat(value, response):
    logging.info("chat - %s" % response)
    HISTORIC_SAYS.append({'epoch': int(time.time()*10000), 'response': response, 'query': value})
    if len(HISTORIC_SAYS) > 10:
        del HISTORIC_SAYS[0:len(HISTORIC_SAYS)-10]


class Chat(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/chat', 'chat', chat, methods=['GET'])
        self.add_url_rule('/api/query', 'query', query, methods=['POST'])
        self.add_url_rule('/api/responses', 'historic', historic, methods=['GET'])
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                for key in [key for key in doc['chatbot'] if key not in ('salutation', 'who')]:
                    conversion = doc['chatbot'][key]
                    for answer in conversion['answers']:
                        for response in conversion['responses']:
                            Robot().training(answer, "say:%s" % response)
                conversion = doc['chatbot']['salutation']
                for response in conversion['responses']:
                    Robot().training(Robot().name, "say:%s" % response)
                conversion = doc['chatbot']['who']
                for answer in conversion['answers']:
                    Robot().training(answer, "say:%s" % Robot().name)
                    for response in conversion['responses']:
                        Robot().training(answer, "say:%s %s" % (response, Robot().name))
            except yaml.YAMLError as exc:
                print(exc)
        Robot().add_event("say", saychat)
