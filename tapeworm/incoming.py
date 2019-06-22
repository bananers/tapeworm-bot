class Incoming:
    def __init__(self, telegram):
        self.telegram = telegram

    @staticmethod
    def parse_message(data):
        if is_command_of(_get_text(data), "ping"):
            return response_text(data["message"], "pong")
        return None

    def handle_data(self, data):
        res = Incoming.parse_message(data)
        if res is None:
            return

        self.telegram.send_text_response(res)


def response_text(src, message):
    return {"chat_id": src["chat"]["id"], "text": message}


def _get_chat_id(data):
    return data["message"]["chat"]["id"]


def _get_text(data):
    return data["message"]["text"]


def is_command(text):
    return text[0] == "/"


def is_command_of(text, command):
    return is_command(text) and command in text
