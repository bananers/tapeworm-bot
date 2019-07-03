from tapeworm.model_link import Link
from tapeworm.incoming import _get_chat_id
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

    incoming.db.links = [create_fake_link(faker) for x in range(0, 11)]
    res = incoming.handle_data(message)
    print(res)
    assert len(res["payload"]["text"].split("\n")) == 10
