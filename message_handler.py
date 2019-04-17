import logging
import urllib

# from utils import create_links_from_message
from services import fetch_last_n_links

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
    return map(lambda x: message['text'][x['offset']:x['offset'] + x['length']],
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

def build_link_line(number, link):
    return u'{0}. [{1}]({2}) by [{3}](tg://user?id={3})' \
        .format(number, link.title, link.link, link.by)

def build_recent_links(src, n=10):    
    links = list(fetch_last_n_links(n))
    number = range(1, len(links)+1)

    body = map(lambda x: build_link_line(x[0], x[1]),
            zip(number, links))

    body_full = u"\n".join(body)  
    return {
        'chat_id': src['chat']['id'],
        'text': u"""
*Last {0} links added*

{1}
        """.format(n, body_full).encode('utf-8').strip(),
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
    
    # url_entities = find_all_url_types(message)
    # create_links_from_message(url_entities) <- call .put() on all values from this method
    
    return None