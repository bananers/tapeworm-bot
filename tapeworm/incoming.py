class Incoming:
    def __init__(self, telegram):
        self.telegram = telegram

    @staticmethod
    def parse_message(data):
        text = _get_text(data)
        if is_command_of(text, "ping"):
            return response_text(data["message"], "pong")
        if is_command_of(text, "help"):
            return help_response(_get_chat_id(data))
        return None

    def handle_data(self, data):
        res = Incoming.parse_message(data)
        if res is None:
            return {"status": "ok"}

        return {"status": "ok", "telegram": self.telegram.send_text_response(res)}


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


def _get_text(data):
    return data["message"]["text"]


def is_command(text):
    return text[0] == "/"


def is_command_of(text, command):
    return is_command(text) and command in text
