import logging
import urllib

from bs4 import BeautifulSoup

from models import Link

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _get_text(m):
    return m['text']

def _get_from(m):
    return m['from']['id']

def respondText(src, message):
    return {
        'chat_id': src['chat']['id'],
        'text': message.encode('utf-8')
    }

def is_command(text):
    return text[0] == "/"

def is_command_of(text, command):
    return is_command(text) and command in text    

def find_all_url_types(message):
    if 'entities' not in message:
        return []        
    return map(lambda x: message['text'][x['offset']:x['length']],
        filter(lambda x: x['type'] == 'url', message['entities']))

def build_help_response(src):
    return {
        'chat_id': src['chat']['id'],
        'text': """
I'm a bot that likes to gobble up links shared by users in the chat. Here's how you can use me.

/links - Shows pages of links that I have gobbled
/ping - Tests whether I'm alive""",
        'parse_mode': 'Markdown',
        'disable_notification': True
    }

def build_recent_links(src, n=10):    
    links = Link.query_all().fetch(n)
    number = range(1, len(links)+1)

    body = map(lambda x: "%d. [%s](%s) by [%d](tg://user?id=%d)" % (x[0], x[1].title, x[1].link, x[1].by, x[1].by),
            zip(number, links))

    return {
        'chat_id': src['chat']['id'],
        'text': """
*Last %d added links*

%s
        """ % (n, "\n".join(body)),
        'parse_mode': 'Markdown',
        'disable_notification': True,
        'disable_web_page_preview': True
    }

def handle_message(message):
    if 'text' not in message:
        return None
        
    text = _get_text(message)
    if is_command_of(text, "ping"):
        return respondText(message, 'pong')
    elif is_command_of(text, "help"):
        return build_help_response(message)
    elif is_command_of(text, "links"):
        return build_recent_links(message)

    url_entities = find_all_url_types(message)
    if len(url_entities) > 0:        
        for url in url_entities:
            body = BeautifulSoup(urllib.urlopen(url))
            title = body.title.string

            link = Link(link=url, title=title, by=_get_from(message))
            link.put()

    return None