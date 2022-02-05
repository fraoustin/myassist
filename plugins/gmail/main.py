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
from icalendar import Calendar
from datetime import datetime
import tempfile
import time

__version__ = "0.0.1"


class GmailProfil(metaclass=Singleton):

    def __init__(self, user, password):
        self.user = user
        self.password = password

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


class CalendarProfil(metaclass=Singleton):

    def __init__(self, calendars=[]):
        self.calendars = calendars

    def _read_from_cal(self, url):
        events = []
        req = urllib.request.Request(url)
        handle = urllib.request.urlopen(req)
        with tempfile.TemporaryDirectory() as tmpdirname:
            path = os.path.join(tmpdirname, "%s.ics" % int(time.time()))
            with open(path, 'wb') as file:
                file.write(handle.read())
            g = open(path, 'rb')
            gcal = Calendar.from_ical(g.read())
            handle.close()
            today = datetime.now().date()
            for component in gcal.walk():
                try:
                    if component.name == "VEVENT":
                        summ = component.get('summary')
                        start = component.get('dtstart').dt
                        end = component.get('dtend').dt
                        if isinstance(start, datetime):
                            if end.date() >= today >= start.date():
                                events.append(summ)
                        else:
                            if end >= today >= start:
                                events.append(summ)
                except Exception:
                    pass
        handle.close()
        return events

    @property
    def events(self):
        events = []
        for calendar in self.calendars:
            events = events + self._read_from_cal(self.calendars[calendar])
        return events


@login_required
def gmail():
    return render_template('gmail.html', user=current_user, plugins=current_app.config['PLUGINS'], gmail=json.loads(ParamApp.getValue("gmail")))


@login_required
def del_gmail():
    gmails = json.loads(ParamApp.getValue("gmail"))
    gmail = request.form.get('gmail')
    if request.form.get('gmail', '') in gmails["calendars"]:
        del gmails["calendars"][request.form.get('gmail', '')]
    paramgmail = ParamApp.get("gmail")
    paramgmail.value = json.dumps(gmails)
    paramgmail.save()
    CalendarProfil.calendars = gmails["calendars"]
    logging.info("gmail - del calendar %s" % gmail)
    return {'status': 'ok'}, 200


@login_required
def add_gmail():
    gmails = json.loads(ParamApp.getValue("gmail"))
    gmails["calendars"][request.form.get('name')] = request.form.get('url')
    paramgmail = ParamApp.get("gmail")
    paramgmail.value = json.dumps(gmails)
    paramgmail.save()
    CalendarProfil.calendars = gmails["calendars"]
    logging.info("gmail - add calendar %s" % request.form.get('name'))
    return {'status': 'ok'}, 200


@login_required
def param_gmail():
    gmails = json.loads(ParamApp.getValue("gmail"))
    gmails["user"] = request.form.get('gmailuser')
    gmails["password"] = request.form.get('gmailpassword')
    paramgmail = ParamApp.get("gmail")
    paramgmail.value = json.dumps(gmails)
    paramgmail.save()
    GmailProfil(user=gmails["user"], password=gmails["password"])
    logging.info("gmail - save param")
    return {'status': 'ok'}, 200


def listengmail(value, response):
    logging.info("gmail - listen number mail")
    Robot().emit_event("", "say:%s" % response.replace("[counter]", str(GmailProfil().emails)))


def listencalendar(value, response):
    logging.info("gmail - listen calendar")
    events = CalendarProfil().events
    if len(events) > 0:
        Robot().emit_event("", "say:%s" % "\n".join(events))


class Gmail(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/gmail', 'gmail', gmail, methods=['GET'])
        self.add_url_rule('/api/gmail/del', 'del_gmail', del_gmail, methods=['POST'])
        self.add_url_rule('/api/gmail/add', 'add_gmail', add_gmail, methods=['POST'])
        self.add_url_rule('/api/gmail/param', 'param_gmail', param_gmail, methods=['POST'])
        Robot().add_event("gmail", listengmail)
        Robot().add_event("calendar", listencalendar)

    def init_db(self):
        if ParamApp.get("gmail") is None:
            db.session.add(ParamApp(key="gmail", value=json.dumps({"user": "", "password": "", "calendars": {}})))
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
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
        GmailProfil(user=gmails["user"], password=gmails["password"])
        CalendarProfil(calendars=gmails["calendars"])
