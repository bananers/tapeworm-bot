import datetime

from enum import Enum
from collections import namedtuple

from google.cloud import datastore

class Kinds(Enum):
    Link = 1

Link = namedtuple('Link', ['link', 'title', 'by', 'date'])

def _create_link_key(client):
    return client.key(Kinds.Link.name)

def create_link(link, title, by, date=None):
    d = datetime.datetime.utcnow() if date is None else date
    return Link(link=link, title=title, by=by, date=d)

def fetch_last_n_links(n):
    client = datastore.Client()
    query = client.query(kind=Kinds.Link.name, order=['-date'])

    for r in query.fetch(limit=n):
        yield create_link(r['link'], r['title'], r['by'], r['date'])

def convert_link_to_entity(client, link):
    key = _create_link_key(client)
    entity = datastore.Entity(key=key)
    entity.update(link._asdict())
    return entity

def insert_links(links):
    client = datastore.Client()
    entities = map(lambda x: convert_link_to_entity(client, x), links)
    client.put_multi(entities)