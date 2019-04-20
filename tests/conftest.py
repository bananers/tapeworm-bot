import pytest

from context import tapeworm

@pytest.fixture
def app():
    app = tapeworm.create_app({
        'TESTING': True
    })

    yield app

@pytest.fixture
def client(app):
    return app.test_client()