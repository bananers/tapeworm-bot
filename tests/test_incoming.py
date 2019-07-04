import pytest

from .conftest import telegram_message_with_text


def test_dispatch_message_on_text(incoming, telegram_message_generator, mocker, faker):
    message = telegram_message_with_text(telegram_message_generator, faker.pystr())

    mocker.patch.object(incoming, "parse_message")
    incoming.handle_data(message)

    incoming.parse_message.assert_called_once()


@pytest.mark.parametrize(
    "data,reason",
    [
        ({}, "should just acknowledge with empty data"),
        (
            {"message": {}},
            "should just acknowledge when message does not contain text key",
        ),
    ],
)
def test_dispatch_unhandled_types_should_just_acknowledge(
    data, reason, incoming, mocker
):
    mocker.patch.object(incoming, "parse_message")
    res = incoming.handle_data(data)

    assert not incoming.parse_message.called, reason
    assert res["status"] == "ok"
