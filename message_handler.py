import logging
import requests

from bs4 import BeautifulSoup

from services import fetch_last_n_links, create_link, insert_links

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

def create_links_from_message(message, url_entities):
    skipped_urls = []
    added_urls = []                
    for url in url_entities:
        logger.debug("Finding title for %s", url)

        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            logger.debug("Unable to retrieve contents of %s got %d", url, res.status_code)
            skipped_urls.append(url)
            continue

        body = BeautifulSoup(res.text)
        title = (body.title.string if body.title is not None else url)
        if not title:
            title = url

        link = create_link(url, title.strip(), _get_from(message))
        added_urls.append(link)
    return (skipped_urls, added_urls)

def build_add_link_response(message, skipped_urls, added_urls):
    added_titles = list(map(lambda x: x.title.strip(), added_urls))

    skipped_urls_by_nl = "\n".join(skipped_urls)
    skipped_url_response = f"*Skipped urls*\n{skipped_urls_by_nl}" if len(skipped_urls) > 0 else ""

    number = range(1, len(added_urls)+1)
    link_line = lambda x: f"{x[0]}. [{x[1].title}]({x[1].link})"
    body = map(link_line,
            zip(number, added_urls))
    body_full = u"\n".join(body)  

    links_added_response = f"*{len(added_titles)} Links added*\n{body_full}" if len(added_titles) > 0 else ""
    return {
        'chat_id': message['chat']['id'],
        'text': u"""
{0}

{1}        
        """.format(skipped_url_response, links_added_response).encode('utf-8').strip(),
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
    skipped_urls, added_urls = create_links_from_message(message, url_entities)
    insert_links(added_urls)
    return build_add_link_response(message, skipped_urls, added_urls)

    return None