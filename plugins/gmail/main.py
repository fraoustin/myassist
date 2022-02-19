from plugins import Plugin
import logging
from robot import Robot, Singleton
from db import db
from db.models import ParamApp
import json
import os
import yaml
from flask import current_app, render_template, request
from flask_login import login_required, current_user
import urllib
import base64
from xml.dom.minidom import parse
from datetime import date
import imaplib
import email

__version__ = "0.0.1"

NOT_EVENTS = "not events"


class GmailProfil(metaclass=Singleton):

    def __init__(self, user, password, fromagenda):
        self._agenda = ""
        self.update(user, password, fromagenda)

    def update(self, user, password, fromagenda):
        self.user = user
        self.password = password
        self.fromagenda = fromagenda
        today = date.today().strftime("%d %b %Y")
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.user, self.password)
            mail.select('inbox')
            type, data = mail.search(None, 'ALL')
            for num in data[0].split():
                rv, data = mail.fetch(num, '(BODY.PEEK[])')
                for response_part in data:
                    msg = email.message_from_bytes(data[0][1])
                    if msg['from'] == self.fromagenda:
                        if today in msg.get("Date"):
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True)
                                    try:
                                        body = body.decode('utf-8')
                                    except Exception:
                                        pass
                                else:
                                    continue
                            body = body.replace("%s ," % self.user, "")
                            try:
                                self._agenda = '\n\r'.join(body.split('\n\r')[:-3])
                            except Exception:
                                pass
                        else:
                            mail.store(num, '+FLAGS', '\\Deleted')
            mail.expunge()
            mail.close()
            mail.logout()
        except Exception:
            pass

    @property
    def emails(self):
        b64auth = base64.b64encode(("%s:%s" % (self.user, self.password)).encode()).decode()
        auth = "Basic " + b64auth
        req = urllib.request.Request("https://mail.google.com/mail/feed/atom/")
        req.add_header("Authorization", auth)
        handle = urllib.request.urlopen(req)
        dom = parse(handle)
        handle.close()
        count_obj = dom.getElementsByTagName("fullcount")[0]
        return int(count_obj.firstChild.wholeText)

    @property
    def agenda(self):
        return self._agenda


@login_required
def gmail():
    return render_template('gmail.html', user=current_user, plugins=current_app.config['PLUGINS'], gmail=json.loads(ParamApp.getValue("gmail")))


@login_required
def param_gmail():
    gmails = json.loads(ParamApp.getValue("gmail"))
    gmails["user"] = request.form.get('gmailuser')
    gmails["password"] = request.form.get('gmailpassword')
    gmails["fromagenda"] = request.form.get('fromagenda')
    paramgmail = ParamApp.get("gmail")
    paramgmail.value = json.dumps(gmails)
    paramgmail.save()
    GmailProfil().update(user=gmails["user"], password=gmails["password"], fromagenda=gmails["fromagenda"])
    logging.info("gmail - save param")
    return {'status': 'ok'}, 200


def listengmail(value, response):
    logging.info("gmail - listen number mail")
    Robot().emit_event("", "say:%s" % response.replace("[counter]", str(GmailProfil().emails)))


def listencalendar(value, response):
    logging.info("gmail - listen number mail")
    Robot().emit_event("", "say:%s" % GmailProfil().agenda)


class Gmail(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/gmail', 'gmail', gmail, methods=['GET'])
        self.add_url_rule('/api/gmail/param', 'param_gmail', param_gmail, methods=['POST'])
        Robot().add_event("gmail", listengmail)
        Robot().add_event("calendar", listencalendar)

    def init_db(self):
        if ParamApp.get("gmail") is None:
            db.session.add(ParamApp(key="gmail", value=json.dumps({"user": "xxxx@gmail.com", "password": "your_password", "fromagenda": "Google Agenda <calendar-notification@google.com>"})))
            db.session.commit()
        gmails = json.loads(ParamApp.getValue("gmail"))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']['gmail']
                for answer in conversion['answers']:
                    for response in conversion['response']:
                        Robot().training(answer, "gmail:%s" % response)
                conversion = doc['chatbot']['calendar']
                for answer in conversion['answers']:
                    Robot().training(answer, "calendar")
                global NOT_EVENTS
                NOT_EVENTS = doc['chatbot']['notfound']['answers'][0]
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
        GmailProfil(user=gmails["user"], password=gmails["password"], fromagenda=gmails["fromagenda"])
