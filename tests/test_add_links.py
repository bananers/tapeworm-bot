import pytest

from tapeworm.incoming import extract_links_from_message
from .conftest import telegram_message_with_links


@pytest.mark.parametrize(
    "message,entities",
    [
        (
            "http://hello.com",
            [{"offset": 0, "length": len("http://hello.com"), "type": "url"}],
        ),
        ("http://google.com", [{"offset": 0, "length": 17, "type": "url"}]),
    ],
)
def test_link_added_when_message_contains_single_link(
    message, entities, incoming, telegram_message_generator
):
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    incoming.handle_data(message_from_telegram)

    incoming.db.create_multi.assert_called_once()
    incoming.telegram.send_text_response.assert_called_once()


@pytest.mark.parametrize(
    "message,entities",
    [
        (
            "http://hello.com google.com",
            [
                {"offset": 0, "length": len("http://hello.com"), "type": "url"},
                {"offset": 18, "length": len("google.com"), "type": "url"},
            ],
        )
    ],
)
def test_link_added_when_message_contains_multiple_links(
    message, entities, incoming, telegram_message_generator
):
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    incoming.handle_data(message_from_telegram)

    incoming.db.create_multi.assert_called_once()
    incoming.telegram.send_text_response.assert_called_once()


@pytest.mark.parametrize(
    "message,entities,expected",
    [
        (
            "http://hello.com",
            [{"offset": 0, "length": len("http://hello.com"), "type": "url"}],
            ["http://hello.com"],
        ),
        (
            "hello.com",
            [{"offset": 0, "length": len("hello.com"), "type": "url"}],
            ["hello.com"],
        ),
    ],
)
def test_link_can_be_extracted(message, entities, expected, telegram_message_generator):
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    res = extract_links_from_message(message_from_telegram)

    assert res == expected
