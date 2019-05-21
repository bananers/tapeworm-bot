# pylint: disable=redefined-outer-name

import pytest

from .context import tapeworm


@pytest.fixture
def app():
    create_app = tapeworm.create_app({"TESTING": True, "WEBHOOK_URL_ID": "random_id"})

    yield create_app


@pytest.fixture
def client(app):
    return app.test_client()
