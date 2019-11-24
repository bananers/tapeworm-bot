# pylint: disable=redefined-outer-name,no-member

import logging
import pytest

from faker import Faker

import tapeworm.ext.telegram as Telegram
import tapeworm.services as services
from tapeworm.incoming import Incoming
from .context import tapeworm
from .fakes import FakeLinks


@pytest.fixture
def app():
    create_app = tapeworm.create_app(
        "test", {"TESTING": True, "WEBHOOK_URL_ID": "random_id"}
    )

    yield create_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def incoming(mocker, extractor):
    telegram = Telegram.TelegramService("zzz")
    links = FakeLinks()

    mocker.patch.object(telegram, "send_text_response")
    mocker.patch.object(telegram, "answer_callback_query")
    mocker.patch.object(telegram, "edit_message_text")
    mocker.patch.object(extractor, "retrieve_url_title")

    return Incoming(telegram, links, extractor, "test")


@pytest.fixture
def extractor() -> services.TitleExtractor:
    extractor = services.TitleExtractor()

    return extractor


@pytest.fixture
def faker():
    logging.getLogger("faker").setLevel(logging.ERROR)
    return Faker()


@pytest.fixture
def telegram_callback_query_generator(faker, telegram_message_generator):
    def _gen():
        return {
            "callback_query": {
                "id": faker.pystr(),
                "data": None,
                "message": telegram_message_generator()["message"],
            }
        }

    return _gen


@pytest.fixture
def telegram_message_generator():
    faker = Faker()

    def _gen():
        return {
            "message": {
                "message_id": faker.pyint(),
                "chat": {"id": faker.pyint()},
                "text": faker.pystr(),
                "from": {"id": faker.pyint(), "username": faker.pystr()},
                "date": int(faker.date_time().timestamp()),
            }
        }

    return _gen


def telegram_callback_query_with_data(generated_update, data):
    generated_update["callback_query"]["data"] = data

    return generated_update


def telegram_message_with_text(gen, text):
    message = gen()
    message["message"]["text"] = text

    return message


def telegram_message_with_links(gen, text, links):
    message = gen()
    message["message"]["text"] = text
    message["message"]["entities"] = links

    return message
