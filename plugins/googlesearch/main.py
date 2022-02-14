from plugins import Plugin
from robot import Robot, logtime
from bs4 import BeautifulSoup
from requests import get
from db.models import ParamApp
import logging
import urllib.parse

__version__ = "0.0.1"


def search(term, num_results=1, lang="en", proxy=None, notfound="notfound"):
    usr_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'}

    def fetch_results(search_term, number_results, language_code):
        escaped_search_term = urllib.parse.quote(search_term)
        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results+1,
                                                                              language_code)
        proxies = None
        if proxy:
            if proxy[:5] == "https":
                proxies = {"https": proxy}
            else:
                proxies = {"http": proxy}

        response = get(google_url, headers=usr_agent, proxies=proxies)
        response.raise_for_status()

        return response.text

    def parse_results(raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        data = soup.find(id='rso').find_all('div')[0]
        if len(data.find_all('span', attrs={'id': 'cwos'})) > 0:
            return data.find_all('span', attrs={'id': 'cwos'})[0].getText(separator=u' ')
        for tag in ['span', 'div']:
            result_block = data.find_all(tag, attrs={'role': 'heading'})
            if len(result_block) > 0:
                if len(result_block) > 1:
                    return result_block[1].getText(separator=u' ')
                if result_block[0].find(tag) is not None:
                    return result_block[0].getText(separator=u' ')
                return result_block[0].getText(separator=u' ')
        if len(data.find_all("div", attrs={'class': 'vmod'})) > 0:
            if len(data.find_all("div", attrs={'class': 'vmod'})[0].find_all("div", attrs={'class': 'vmod'})) > 0:
                response = []
                for elt in data.find_all("div", attrs={'class': 'vmod'})[0].find_all("div", attrs={'class': 'thODed'}):
                    response.append(elt.getText(separator=u' '))
                return ' '.join(response)
        if len(soup.find_all("div", attrs={'class': 'rllt__details'})) > 0:
            response = []
            for elt in soup.find_all("div", attrs={'class': 'rllt__details'})[0].find_all("div"):
                response.append(elt.getText(separator=u' '))
            return ' '.join(response)
        if len(data.find_all('div', attrs={'id': 'NotFQb'})) > 0:
            return data.find('div', attrs={'id': 'NotFQb'}).find('input')['value']
        if len(data.find_all('div', attrs={'class': 'gws-csf-randomnumber__result'})) > 0:
            return data.find('div', attrs={'class': 'gws-csf-randomnumber__result'}).getText(separator=u' ')
        if len(data.find_all('div', attrs={'id': 'tw-target-text-container'})) > 0:
            return data.find('div', attrs={'id': 'tw-target-text-container'}).getText(separator=u' ')
        return notfound

    html = fetch_results(term, num_results, lang)
    return parse_results(html)


@logtime
def googlesearch(value, response):
    response = search(value, lang=ParamApp.getValue("basic_langue"))
    logging.info("googlesearch - %s -> %s" % (value, response))
    if response == 'notfound':
        Robot().query(response)
    else:
        Robot().emit_event(value, "say:%s" % response)


class Googlesearch(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, icon=False, *args, **kw)
        Robot().add_event("notfound", googlesearch)
