from collections import namedtuple
from google.cloud import datastore

Link = namedtuple("Link", ["id", "link", "title", "by", "date"])


def get_client():
    return datastore.Client("tapeworm-bot")


def from_datastore(entity):
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()

    return Link(
        id=entity.key.id,
        link=entity["link"],
        title=entity["title"],
        by=entity["by"],
        date=entity["date"],
    )


def from_dict(data):
    """
    Creates a Link from a dictionary. The output from this function
    can be passed into create with Link._asdict()
    """
    if not isinstance(data, dict):
        raise ValueError("data must be type of dict")
    if not data:
        raise ValueError("data must be valid")

    return Link(
        id=None,
        link=data["link"],
        title=data["title"],
        by=data["by"],
        date=data["date"],
    )


def create(data):
    if not isinstance(data, Link):
        raise ValueError("data must be type of Link")

    ds = get_client()
    key = ds.key("Link")

    entity = datastore.Entity(key=key)
    entity.update(data)
    ds.put(entity)

    return from_datastore(entity)


def create_multi(datas):
    if not isinstance(datas, list):
        raise ValueError("datas must be type of List containing Link")

    ds = get_client()
    with ds.batch() as batch:
        for data in datas:
            entity = datastore.Entity(key=ds.key("Link"))
            entity.update(data._asdict())
            batch.put(entity)
            yield from_datastore(entity)


def list_links(limit=10, offset=0):
    ds = get_client()

    query = ds.query(kind="Link", order=["-date"])
    query_iterator = query.fetch(limit=limit, offset=offset)
    page = next(query_iterator.pages)

    entities = list(map(from_datastore, page))
    return entities


def read(identifier):
    if not identifier:
        raise ValueError("id is not valid")
    ds = get_client()
    key = ds.key("Link", int(identifier))
    return from_datastore(ds.get(key))
