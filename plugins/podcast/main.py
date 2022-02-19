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
import feedparser

__version__ = "0.0.1"


@login_required
def podcast():
    return render_template('podcast.html', user=current_user, plugins=current_app.config['PLUGINS'], podcasts=json.loads(ParamApp.getValue("podcast")))


@login_required
def del_podcast():
    podcasts = json.loads(ParamApp.getValue("podcast"))
    podcast = request.form.get('podcast')
    url = podcasts[podcast]
    if request.form.get('podcast', '') in podcasts:
        del podcasts[request.form.get('podcast', '')]
    parampodcast = ParamApp.get("podcast")
    parampodcast.value = json.dumps(podcasts)
    parampodcast.save()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["podcast"]
            Robot().remove_training(podcast, "podcast:%s" % url)
            for answer in conversion['answers']:
                Robot().remove_training("%s %s" % (answer, podcast), "podcast:%s" % url)
            for answer in conversion['stop']:
                Robot().remove_training("%s %s" % (answer, podcast), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("podcast - del %s" % podcast)
    return {'status': 'ok'}, 200


@login_required
def add_podcast():
    podcasts = json.loads(ParamApp.getValue("podcast"))
    podcasts[request.form.get('name')] = request.form.get('url')
    parampodcast = ParamApp.get("podcast")
    parampodcast.value = json.dumps(podcasts)
    parampodcast.save()
    podcast = request.form.get('name')
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
        try:
            doc = yaml.safe_load(stream)
            conversion = doc['chatbot']["podcast"]
            Robot().training(podcast, "podcast:%s" % podcasts[podcast])
            for answer in conversion['answers']:
                Robot().training("%s %s" % (answer, podcast), "podcast:%s" % podcasts[podcast])
            for answer in conversion['stop']:
                Robot().training("%s %s" % (answer, podcast), "stop")
        except yaml.YAMLError as exc:
            print("!!!!! ERROR")
            print(exc)
    logging.info("podcast - add %s" % request.form.get('name'))
    return {'status': 'ok'}, 200


def listenpodcast(value, response):
    logging.info("podcast - listen %s" % response)
    feed = feedparser.parse(response)
    link = [link['href'] for link in feed.entries[0].links if link['href'].endswith(".mp3") is True][0]
    logging.debug("podcast - listen feed %s" % link)
    Robot()._stopsound()
    Robot()._queue_playsound(link)


class Podcast(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.add_url_rule('/podcast', 'podcast', podcast, methods=['GET'])
        self.add_url_rule('/api/podcast/del', 'del_podcast', del_podcast, methods=['POST'])
        self.add_url_rule('/api/podcast/add', 'add_podcast', add_podcast, methods=['POST'])
        Robot().add_event("podcast", listenpodcast)

    def init_db(self):
        if ParamApp.get("podcast") is None:
            db.session.add(ParamApp(key="podcast", value=json.dumps({})))
            db.session.commit()
        podcasts = json.loads(ParamApp.getValue("podcast"))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']["podcast"]
                for podcast in podcasts.keys():
                    Robot().training(podcast, "podcast:%s" % podcasts[podcast])
                    for answer in conversion['answers']:
                        Robot().training("%s %s" % (answer, podcast), "podcast:%s" % podcasts[podcast])
                for podcast in podcasts.keys():
                    for answer in conversion['stop']:
                        Robot().training("%s %s" % (answer, podcast), "stop")
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
