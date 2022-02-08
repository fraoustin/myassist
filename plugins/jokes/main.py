from plugins import Plugin
from robot import Robot
from requests import get
import os
import yaml
import pyjokes

__version__ = "0.0.1"


def joke(value, response):
    lang = Robot().mic.langue.split('-')[0]
    if lang in ('en', 'de', 'es', 'gl', 'eus'):
        joke = pyjokes.get_joke(language='')
    elif lang == 'fr':
        usr_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'}
        response = get("https://www.blagues-api.fr/", headers=usr_agent)
        dataOne = response.text.split('",joke:"')[1].split('",answer:"')[0]
        dataTwo = response.text.split('",answer:"')[1].split('"}')[0]
        joke = dataOne + " ... " + dataTwo
    else:
        joke = pyjokes.get_joke(language='en')
    Robot().emit_event("", "say:%s" % joke)


class Jokes(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("joke", joke)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                conversion = doc['chatbot']['jokes']
                for answer in conversion['answers']:
                    Robot().training(answer, "joke")
            except yaml.YAMLError as exc:
                print("!!!!! ERROR")
                print(exc)
