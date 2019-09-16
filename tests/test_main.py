from .context import tapeworm


def test_config():
    assert not tapeworm.create_app("not_test").testing
    assert tapeworm.create_app("test", {"TESTING": True}).testing


def test_hello(client):
    res = client.get("/")
    assert res.data == b"ok"


def test_urls(app):
    # https://stackoverflow.com/questions/31710064/testing-flask-routes-do-and-dont-exist
    adapter = app.url_map.bind("")

    adapter.match("/me", method="GET")
    adapter.match("/info_webhook", method="GET")
    adapter.match("/updates", method="GET")
    adapter.match("/webhook", method="POST")
    adapter.match("/webhook", method="DELETE")
    adapter.match("/webhook_" + app.config["WEBHOOK_URL_ID"], method="POST")
