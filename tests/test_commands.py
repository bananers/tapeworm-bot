from tapeworm.incoming import _get_chat_id, help_response

from .conftest import telegram_message_with_text


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


def test_links_command_sends_response(incoming, telegram_message_generator):
    message = telegram_message_with_text(telegram_message_generator, "/links")

    incoming.handle_data(message)

    incoming.telegram.send_text_response.assert_called_once()


def test_unknown_command_doesnt_send_response(incoming, telegram_message_generator):
    message = telegram_message_generator()

    res = incoming.handle_data(message)

    incoming.telegram.send_text_response.assert_not_called()
    assert res["status"] == "ok"
