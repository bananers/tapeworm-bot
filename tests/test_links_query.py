import pytest

from tapeworm.model_link import Link
from tapeworm.incoming import _get_chat_id, links_response
from .conftest import telegram_message_with_text


def test_should_inform_when_no_links(incoming, telegram_message_generator):
    message = telegram_message_with_text(telegram_message_generator, "/links")

    res = incoming.handle_data(message)
    assert res["payload"]["text"] == "No links found"


def test_should_display_one_link(incoming, telegram_message_generator, faker):
    message = telegram_message_with_text(telegram_message_generator, "/links")

    incoming.db.links = [create_fake_link(faker)]
    link = incoming.db.links[0]
    res = incoming.handle_data(message)

    assert res["payload"]["chat_id"] == _get_chat_id(message)
    assert (
        res["payload"]["text"]
        == f"1. <a href='{link.link}'>{link.title}</a> by {link.by}"
    )


def create_fake_link(faker) -> Link:
    return Link(
        faker.pyint(), faker.pystr(), faker.pystr(), faker.pyint(), faker.date_time()
    )


def test_should_display_maximally_10_links(incoming, telegram_message_generator, faker):
    message = telegram_message_with_text(telegram_message_generator, "/links")

    incoming.db.links = [
        create_fake_link(faker) for x in range(0, faker.pyint(min=10 + 1, max=100))
    ]
    res = incoming.handle_data(message)

    assert len(res["payload"]["text"].split("\n")) == 10


@pytest.mark.parametrize(
    "links,expected",
    [
        ([], "No links found"),
        (
            [Link(1, "www.test.com", "Test", "henlo", None)],
            "1. <a href='www.test.com'>Test</a> by henlo",
        ),
        (
            [
                Link(1, "www.test.com", "Test", "henlo", None),
                Link(1, "www.test.com", "Test", "henlo", None),
                Link(1, "www.test.com", "Test", "henlo", None),
            ],
            "1. <a href='www.test.com'>Test</a> by henlo"
            + "\n"
            + "2. <a href='www.test.com'>Test</a> by henlo"
            + "\n"
            + "3. <a href='www.test.com'>Test</a> by henlo",
        ),
    ],
)
def test_links_response(links, expected, faker):
    res = links_response(faker.pyint(), links)

    assert res["text"] == expected
