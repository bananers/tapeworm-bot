import logging

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

def handle_message(message):
    text = _get_text(message)
    if is_command_of(text, "ping"):
        return respondText(message, 'pong')

    url_entities = find_all_url_types(message)
    if len(url_entities) > 0:        
        for url in url_entities:
            link = Link(link=url, by=_get_from(message))
            link.put()
        return respondText(message, "%d links added" % (len(url_entities)))

    return None