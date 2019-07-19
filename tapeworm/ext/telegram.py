# pylint: disable=no-member

import json
import logging
import requests

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, telegram_url):
        self.telegram_url = telegram_url

    def _send_response(self, endpoint, payload):
        res = requests.post(self.telegram_url + endpoint, data=payload)
        res.raise_for_status()
        return {
            "payload": payload,
            "endpoint": endpoint,
            "status_code": res.status_code,
            "response": json.loads(res.text),
        }

    def send_text_response(self, payload):
        return self._send_response("sendMessage", payload)

    def answer_callback_query(self, payload):
        return self._send_response("answerCallbackQuery", payload)

    def edit_message_text(self, payload):
        return self._send_response("editMessageText", payload)
