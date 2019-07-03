from .conftest import telegram_message_with_text


def test_dispatch_message(incoming, telegram_message_generator, mocker, faker):
    message = telegram_message_with_text(telegram_message_generator, faker.pystr())

    mocker.patch.object(incoming, "parse_message")
    incoming.handle_data(message)

    incoming.parse_message.assert_called_once()


def test_dispatch_unhandled_types_should_just_acknowledge(incoming, mocker):
    data = {}

    mocker.patch.object(incoming, "parse_message")
    res = incoming.handle_data(data)

    assert not incoming.parse_message.called
    assert res["status"] == "ok"
