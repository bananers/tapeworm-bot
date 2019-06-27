from datetime import datetime
from .services import UnableToObtainTitleError


class Incoming:
    def __init__(self, telegram, db, services):
        self.telegram = telegram
        # pylint: disable=invalid-name
        self.db = db
        self.services = services

    def parse_message(self, data):
        text = _get_text(data)
        if is_command_of(text, "ping"):
            return response_text(data["message"], "pong")
        if is_command_of(text, "help"):
            return help_response(_get_chat_id(data))
        if contains_links(data):
            return self.extract_and_add_links(data)

        return None

    def extract_and_add_links(self, data):
        urls_in_message = extract_links_from_message(data)
        if urls_in_message:
            extracted_urls = []
            skipped_urls = []
            for url in urls_in_message:
                try:
                    item_added = self.db.from_dict(
                        {
                            "link": url,
                            "by": _get_author(data),
                            "title": self.services.retrieve_url_title(url),
                            "date": _get_message_date(data),
                        }
                    )
                    extracted_urls.append(item_added)
                except UnableToObtainTitleError as _error:
                    skipped_urls.append(url)
            created_links = self.db.create_multi(extracted_urls)
            return link_added_response(_get_chat_id(data), created_links, skipped_urls)
        return None

    def handle_data(self, data):
        res = self.parse_message(data)
        if res is None:
            return {"status": "ok"}

        return {"status": "ok", "telegram": self.telegram.send_text_response(res)}


def contains_links(message):
    message = message["message"]
    if "entities" not in message:
        return False

    return (
        next(filter(lambda x: x["type"] == "url", message["entities"]), None)
        is not None
    )


def extract_links_from_message(message):
    message = message["message"]
    if "entities" not in message:
        return []
    return list(
        map(
            lambda x: message["text"][x["offset"] : x["offset"] + x["length"]],
            filter(lambda x: x["type"] == "url", message["entities"]),
        )
    )


def link_added_response(sender_chat_id, items_added, items_skipped):
    title_link = lambda index, title: f"{index}. {title}"
    items_added_body = (
        "<b>Links added</b>\n"
        + "\n".join(
            map(
                lambda x: title_link(*x),
                zip(range(1, len(items_added) + 1), items_added),
            )
        )
        + "\n"
    )
    items_skipped_body = (
        "<b>Links skipped</b>\n"
        + "\n".join(
            map(
                lambda x: title_link(*x),
                zip(range(1, len(items_skipped) + 1), items_skipped),
            )
        )
        + "\n"
    )
    body = ""
    if items_added:
        body += items_added_body
    if items_skipped:
        body += items_skipped_body
    return {
        "chat_id": sender_chat_id,
        "text": body,
        "parse_mode": "HTML",
        "disable_notification": True,
        "disable_web_page_preview": True,
    }


def help_response(sender_chat_id):
    return {
        "chat_id": sender_chat_id,
        "text": """
I'm a bot that likes to gobble up links shared by users in the chat. Here's how you can use me.

/links - Shows pages of links that I have gobbled
/ping - Tests whether I'm alive
""",
        "parse_mode": "Markdown",
        "disable_notification": True,
    }


def response_text(src, message):
    return {"chat_id": src["chat"]["id"], "text": message}


def _get_chat_id(data):
    return data["message"]["chat"]["id"]


def _get_author(data):
    return data["message"]["from"]["id"]


def _get_message_date(data):
    return datetime.utcfromtimestamp(data["message"]["date"])


def _get_text(data):
    return data["message"]["text"]


def is_command(text):
    return text[0] == "/"


def is_command_of(text, command):
    return is_command(text) and command in text
