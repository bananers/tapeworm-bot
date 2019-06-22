# pylint: disable=no-member,redefined-outer-name
import pytest
from faker import Faker

import tapeworm.ext.telegram as Telegram
from tapeworm.incoming import Incoming, _get_chat_id, help_response


@pytest.fixture
def telegram_message_generator():
    faker = Faker()

    def _gen():
        return {"message": {"chat": {"id": faker.pyint()}, "text": faker.pystr()}}

    return _gen


def telegram_message_with_text(gen, text):
    message = gen()
    message["message"]["text"] = text

    return message


@pytest.fixture
def incoming(mocker):
    telegram = Telegram.TelegramService("zzz")
    mocker.patch.object(telegram, "send_text_response")
    return Incoming(telegram)


def test_ping_command_sends_response(incoming, telegram_message_generator):
    message = telegram_message_with_text(telegram_message_generator, "/ping")

    incoming.handle_data(message)

    incoming.telegram.send_text_response.assert_called_once_with(
        {"chat_id": _get_chat_id(message), "text": "pong"}
    )


def test_help_command_sends_response(incoming, telegram_message_generator):
    message = telegram_message_with_text(telegram_message_generator, "/help")

    incoming.handle_data(message)

    incoming.telegram.send_text_response.assert_called_once_with(
        help_response(_get_chat_id(message))
    )


def test_unknown_command_doesnt_send_response(incoming, telegram_message_generator):
    message = telegram_message_generator()

    res = incoming.handle_data(message)

    incoming.telegram.send_text_response.assert_not_called()
    assert res["status"] == "ok"
