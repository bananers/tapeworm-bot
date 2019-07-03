import pytest

from tapeworm.incoming import extract_links_from_message, link_added_response
from tapeworm.services import UnableToObtainTitleError
from tapeworm.model_link import Link
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
    message, entities, incoming, telegram_message_generator, faker
):
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    incoming.extractor.retrieve_url_title.side_effect = faker.pystr()
    incoming.handle_data(message_from_telegram)

    incoming.telegram.send_text_response.assert_called_once()
    assert len(incoming.db.links) == len(entities)


@pytest.mark.parametrize(
    "message,entities",
    [
        (
            "http://hello.com google.com",
            [
                {"offset": 0, "length": len("http://hello.com"), "type": "url"},
                {
                    "offset": len("http://hello.com") + 1,
                    "length": len("google.com"),
                    "type": "url",
                },
            ],
        )
    ],
)
def test_link_added_when_message_contains_multiple_links(
    message, entities, incoming, telegram_message_generator, faker
):
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    incoming.extractor.retrieve_url_title.side_effect = faker.pystr()
    incoming.handle_data(message_from_telegram)

    incoming.telegram.send_text_response.assert_called_once()
    assert len(incoming.db.links) == len(entities)


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
        ("qwpoekqwekpqwoeqpkqpoekqwpeqsa asdpokaspdokasp okaspo kdaspdkas", [], []),
    ],
)
def test_link_can_be_extracted(message, entities, expected, telegram_message_generator):
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    res = extract_links_from_message(message_from_telegram)

    assert res == expected


def test_invalid_titles_have_response(incoming, telegram_message_generator):
    message = "http://hello.com"
    entities = [{"offset": 0, "length": len(message), "type": "url"}]
    message_from_telegram = telegram_message_with_links(
        telegram_message_generator, message, entities
    )

    incoming.extractor.retrieve_url_title.side_effect = UnableToObtainTitleError
    incoming.handle_data(message_from_telegram)

    incoming.telegram.send_text_response.assert_called_once()


@pytest.mark.parametrize(
    "titles,expected",
    [
        ([Link(None, None, "Hello", None, None)], "1. Hello"),
        (
            [
                Link(None, None, "link1", None, None),
                Link(None, None, "link2", None, None),
            ],
            "1. link1\n2. link2",
        ),
    ],
)
def test_link_response_for_links_added_response(faker, titles, expected):
    res = link_added_response(faker.pyint(), titles, [])

    assert res["text"] == f"""<b>Links added</b>\n{expected}\n"""


@pytest.mark.parametrize(
    "skipped_urls,expected",
    [(["Hello"], "1. Hello"), (["link1", "link2"], "1. link1\n2. link2")],
)
def test_link_response_for_skipped_links_response(faker, skipped_urls, expected):
    res = link_added_response(faker.pyint(), [], skipped_urls)

    assert res["text"] == f"""<b>Links skipped</b>\n{expected}\n"""


@pytest.mark.parametrize(
    "added,skipped,expected",
    [
        (
            [Link(None, None, "link1", None, None)],
            ["link2"],
            """<b>Links added</b>
1. link1
<b>Links skipped</b>
1. link2
""",
        )
    ],
)
def test_link_response(faker, added, skipped, expected):
    res = link_added_response(faker.pyint(), added, skipped)

    assert res["text"] == expected
