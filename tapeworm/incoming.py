import json
import logging

from datetime import datetime
from .services import UnableToObtainTitleError
from .model_link import Links

logger = logging.getLogger(__name__)

PAGINATION_PREV_INDEX = 0
PAGINATION_PAGE_INDEX = 1
PAGINATION_NEXT_INDEX = 2

DEFAULT_LIMIT = 10


class Incoming:
    def __init__(self, telegram, db, extractor, project_id):
        self.telegram = telegram
        # pylint: disable=invalid-name
        self.db = db
        self.extractor = extractor
        self.project_id = project_id

    def parse_message(self, data):
        text = _get_text(data)
        if is_command_of(text, "ping"):
            return response_text(data["message"], "pong")
        if is_command_of(text, "links"):
            return links_response(
                _get_chat_id(data),
                self.db.list_links(0, DEFAULT_LIMIT),
                0,
                DEFAULT_LIMIT,
            )
        if is_command_of(text, "web"):
            return web_response(_get_chat_id(data), self.project_id)
        if is_command_of(text, "help"):
            return help_response(_get_chat_id(data))
        if contains_links(data):
            return self.extract_and_add_links(data)

        return None

    def parse_callback_query(self, callback_query):
        if "data" not in callback_query:
            return None
        data = _get_cq_data(callback_query)
        if data is None:
            return None

        args = data.split(":")
        if len(args) != 3:
            return None

        if not args[2].isdigit():
            return None

        self.telegram.answer_callback_query({"callback_query_id": callback_query["id"]})

        offset = int(args[2])
        links = self.db.list_links(offset, DEFAULT_LIMIT)
        if offset != 0 and not links:
            return None

        return dict(
            {"message_id": _get_message_id(callback_query)},
            **links_response(
                _get_chat_id(callback_query), links, offset, DEFAULT_LIMIT
            ),
        )

    def extract_and_add_links(self, data):
        urls_in_message = extract_links_from_message(data)
        if urls_in_message:
            extracted_urls = []
            skipped_urls = []
            for url in urls_in_message:
                try:
                    title, req_url = self.extractor.retrieve_url_title(url)
                    item_added = Links.from_dict(
                        {
                            "link": req_url,
                            "by": _get_userid(data),
                            "by_username": _get_username(data),
                            "title": title,
                            "date": _get_message_date(data),
                        }
                    )
                    extracted_urls.append(item_added)
                except UnableToObtainTitleError as _error:
                    skipped_urls.append(url)
            created_links = list(self.db.create_multi(extracted_urls))
            return link_added_response(_get_chat_id(data), created_links, skipped_urls)
        return None

    def _send_response(self, res, func):
        logger.debug("Sending response", extra={"payload": res})
        return {
            "status": "ok",
            "payload": res,
            "telegram": func(res) if res is not None else None,
        }

    def handle_data(self, data):
        if "message" in data:
            message = data["message"]
            if "text" in message:
                res = self.parse_message(data)
                return self._send_response(res, self.telegram.send_text_response)

        if "callback_query" in data:
            res = self.parse_callback_query(data["callback_query"])
            return self._send_response(res, self.telegram.edit_message_text)

        return {"status": "ok"}


URL_FILTER = lambda x: x["type"] == "url"


def contains_links(message):
    message = message["message"]
    if "entities" not in message:
        return False

    return next(filter(URL_FILTER, message["entities"]), None) is not None


def extract_links_from_message(message):
    message = message["message"]
    if "entities" not in message:
        return []
    return list(
        map(
            lambda x: message["text"][x["offset"] : x["offset"] + x["length"]],
            filter(URL_FILTER, message["entities"]),
        )
    )


def links_response(sender_chat_id, links, offset, limit):
    link_to_str = (
        lambda index, link: f"{index}. <a href='{link.link}'>{link.title}</a> by {link.by_username}"
    )
    display_links = links[:limit]
    links_body = "\n".join(
        map(
            lambda x: link_to_str(*x),
            zip(range(1, len(display_links) + 1), display_links),
        )
    )
    return {
        "chat_id": sender_chat_id,
        "text": links_body if links else "No links found",
        "parse_mode": "HTML",
        "disable_notification": True,
        "disable_web_page_preview": True,
        "reply_markup": json.dumps(
            {"inline_keyboard": pagination_builder(links, offset, limit)}
        ),
    }


def button(text, data):
    return {"text": text, "callback_data": data}


def pagination_builder(links, offset, limit):
    if not links:
        return []
    page_number = int(offset / limit) + 1

    has_previous = offset > 0
    back_button_text = f"<{limit}" if has_previous else "<0"
    back_button_data = f"links:p:{offset-limit}" if has_previous else "links:noop"

    next_button_text = f">{limit}"
    next_button_data = f"links:n:{offset+limit}"
    return [
        [
            button(back_button_text, back_button_data),
            button(str(page_number), "links:noop"),
            button(next_button_text, next_button_data),
        ]
    ]


def link_added_response(sender_chat_id, items_added, items_skipped):
    link_to_str = lambda index, link: f"{index}. {link.title}"
    items_added_body = (
        "<b>Links added</b>\n"
        + "\n".join(
            map(
                lambda x: link_to_str(*x),
                zip(range(1, len(items_added) + 1), items_added),
            )
        )
        + "\n"
    )
    title_link = lambda index, title: f"{index}. {title}"
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


def web_response(sender_chat_id, project_id):
    return {
        "chat_id": sender_chat_id,
        "text": f"https://{project_id}.appspot.com/links",
        "disable_notification": True,
    }


def help_response(sender_chat_id):
    return {
        "chat_id": sender_chat_id,
        "text": """
I'm a bot that likes to gobble up links shared by users in the chat. Here's how you can use me.

/links - Shows pages of links that I have gobbled
/ping - Tests whether I'm alive
/web - Provides you the URL to where the interface lives
""",
        "parse_mode": "Markdown",
        "disable_notification": True,
    }


def response_text(src, message):
    return {"chat_id": src["chat"]["id"], "text": message}


def _get_chat_id(data):
    return data["message"]["chat"]["id"]


def _get_message_id(data):
    return data["message"]["message_id"]


def _get_userid(data):
    return data["message"]["from"]["id"]


def _get_username(data):
    return data["message"]["from"]["username"]


def _get_message_date(data):
    return datetime.utcfromtimestamp(data["message"]["date"])


def _get_text(data):
    return data["message"]["text"]


def _get_cq_data(data):
    return data["data"]


def is_command(text):
    return text[0] == "/"


def is_command_of(text, command):
    return is_command(text) and command in text
