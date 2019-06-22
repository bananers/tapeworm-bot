# pylint: disable=no-member

import json
import logging
import requests

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, telegram_url):
        self.telegram_url = telegram_url

    def send_text_response(self, payload):
        res = requests.post(self.telegram_url + "sendMessage", data=payload)
        res.raise_for_status()
        return {
            "payload": payload,
            "status_code": res.status_code,
            "response": json.loads(res.text),
        }
