import configparser

from bs4 import BeautifulSoup
# from google.appengine.api import urlfetch

# from models import Link

def parse_config(telegram_base_url, file="config.ini"):
    config = configparser.ConfigParser()
    config.read(file)

    return {
        'token': config.get("bot", "token"),
        'telegram_url': telegram_base_url + config.get("bot", "token") + "/",
        'project_id': config.get("bot", "project_id"),
        'webhook_url_id': config.get("bot", "webhook_url_id")
    }

# def create_links_from_message(url_entities):
#     if len(url_entities) > 0:                
#             for url in url_entities:
#                 logger.debug("Finding title for %s" % url)
#                 try:
#                     res = urlfetch.fetch(url)
#                     if res.status_code != 200:
#                         continue
#                     body = BeautifulSoup(res.content)
#                     title = (body.title.string if body.title is not None else url).strip()

#                     link = Link(link=url, title=title, by=_get_from(message))
#                     yield link
#                 except urlfetch.Error as e:
#                     logger.exception('Exception while fetching ' + url)