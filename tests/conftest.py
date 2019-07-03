# pylint: disable=redefined-outer-name,no-member

import pytest

from faker import Faker

import tapeworm.ext.telegram as Telegram
import tapeworm.services as services
from tapeworm.incoming import Incoming
from .context import tapeworm
from .fakes import FakeLinks


@pytest.fixture
def app():
    create_app = tapeworm.create_app({"TESTING": True, "WEBHOOK_URL_ID": "random_id"})

    yield create_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def incoming(mocker, extractor):
    telegram = Telegram.TelegramService("zzz")
    links = FakeLinks()

    mocker.patch.object(telegram, "send_text_response")
    mocker.patch.object(extractor, "retrieve_url_title")

    return Incoming(telegram, links, extractor)


@pytest.fixture
def extractor() -> services.TitleExtractor:
    extractor = services.TitleExtractor()

    return extractor


@pytest.fixture
def faker():
    return Faker()


@pytest.fixture
def telegram_message_generator():
    faker = Faker()

    def _gen():
        return {
            "message": {
                "chat": {"id": faker.pyint()},
                "text": faker.pystr(),
                "from": {"id": faker.pyint()},
                "date": int(faker.date_time().timestamp()),
            }
        }

    return _gen


def telegram_message_with_text(gen, text):
    message = gen()
    message["message"]["text"] = text

    return message


def telegram_message_with_links(gen, text, links):
    message = gen()
    message["message"]["text"] = text
    message["message"]["entities"] = links

    return message
