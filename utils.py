
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch

from models import Link

def create_links_from_message(url_entities):
    if len(url_entities) > 0:                
            for url in url_entities:
                logger.debug("Finding title for %s" % url)
                try:
                    res = urlfetch.fetch(url)
                    if res.status_code != 200:
                        continue
                    body = BeautifulSoup(res.content)
                    title = (body.title.string if body.title is not None else url).strip()

                    link = Link(link=url, title=title, by=_get_from(message))
                    yield link
                except urlfetch.Error as e:
                    logger.exception('Exception while fetching ' + url)