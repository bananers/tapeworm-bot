import json
import pytest

from tapeworm.model_link import Link
from tapeworm.incoming import (
    _get_chat_id,
    links_response,
    pagination_builder,
    PAGINATION_PAGE_INDEX,
    PAGINATION_PREV_INDEX,
    PAGINATION_NEXT_INDEX,
    DEFAULT_LIMIT,
)
from .conftest import telegram_message_with_text
from .assertions import assert_button_text, assert_button_callback_data


def test_should_inform_when_no_links(incoming, telegram_message_generator):
    message = telegram_message_with_text(telegram_message_generator, "/links")

    res = incoming.handle_data(message)
    assert res["payload"]["text"] == "No links found"


def create_fake_link(faker) -> Link:
    return Link(
        faker.pyint(), faker.pystr(), faker.pystr(), faker.pyint(), faker.date_time()
    )


def create_n_fake_link(faker, n_links) -> [Link]:
    return [create_fake_link(faker) for x in range(n_links)]


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


def test_should_display_maximally_10_links(incoming, telegram_message_generator, faker):
    message = telegram_message_with_text(telegram_message_generator, "/links")

    incoming.db.links = [
        create_fake_link(faker) for x in range(0, faker.pyint(min=10 + 1, max=100))
    ]
    res = incoming.handle_data(message)

    assert len(res["payload"]["text"].split("\n")) == DEFAULT_LIMIT


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
    res = links_response(faker.pyint(), links, 0, 10)

    assert res["text"] == expected


def test_pagination_page_indicator_when_empty():
    links = []
    offset = 0
    limit = 10

    markup = pagination_builder(links, offset, limit)
    assert not markup, "No navigation buttons should be shown when there are no links"


def test_pagination_page_indicator_with_items(faker):
    links = create_n_fake_link(faker, faker.pyint(min=1, max=20))
    offset = 0
    limit = 10

    markup = pagination_builder(links, offset, limit)

    assert markup, "Should display navigation buttons when there are items"
    assert_button_text(markup[0][PAGINATION_PAGE_INDEX], "1")
    assert_button_callback_data(markup[0][PAGINATION_PAGE_INDEX], "links:noop")


@pytest.mark.parametrize(
    "n_links,offset,limit,expected", [(20, 10, 10, 2), (20, 9, 10, 1), (10, 0, 10, 1)]
)
def test_pagination_page_indicator_with_items_on_offset(
    n_links, offset, limit, expected, faker
):
    links = create_n_fake_link(faker, n_links)

    markup = pagination_builder(links, offset, limit)

    assert_button_text(markup[0][PAGINATION_PAGE_INDEX], str(expected))


def test_links_response_should_include_pagination_indicator(faker):
    offset = 0
    limit = 10

    res = links_response(
        faker.pyint(), [Link(1, "www.test.com", "Test", "henlo", None)], offset, limit
    )
    markup = json.loads(res["reply_markup"])

    assert res["reply_markup"] is not None
    assert_button_text(markup["inline_keyboard"][0][PAGINATION_PAGE_INDEX], "1")


# pylint:disable=too-many-arguments
@pytest.mark.parametrize(
    "n_links,offset,limit,expected,prev_offset",
    [
        (10, 0, 10, "<0", "links:noop"),
        (10, 5, 5, "<0", "links:p:0"),
        (50, 20, 5, "<15", "links:p:15"),
        (10, 2, 2, "<0", "links:p:0"),
    ],
)
def test_links_response_should_include_back_button(
    n_links, offset, limit, expected, prev_offset, faker
):
    res = links_response(
        faker.pyint(), create_n_fake_link(faker, n_links), offset, limit
    )
    markup = json.loads(res["reply_markup"])

    assert_button_text(markup["inline_keyboard"][0][PAGINATION_PREV_INDEX], expected)
    assert_button_callback_data(
        markup["inline_keyboard"][0][PAGINATION_PREV_INDEX], prev_offset
    )


# pylint:disable=too-many-arguments
@pytest.mark.parametrize(
    "n_links,offset,limit,expected,prev_offset",
    [
        (10, 0, 10, ">10", "links:n:10"),
        (4, 0, 2, ">2", "links:n:2"),
        (5, 0, 10, ">0", "links:noop"),
    ],
)
def test_links_response_should_include_next_button(
    n_links, offset, limit, expected, prev_offset, faker
):
    res = links_response(
        faker.pyint(), create_n_fake_link(faker, n_links), offset, limit
    )
    markup = json.loads(res["reply_markup"])

    assert_button_text(markup["inline_keyboard"][0][PAGINATION_NEXT_INDEX], expected)
    assert_button_callback_data(
        markup["inline_keyboard"][0][PAGINATION_NEXT_INDEX], prev_offset
    )
