from context import tapeworm

def test_config():
    assert not tapeworm.create_app().testing
    assert tapeworm.create_app({'TESTING': True}).testing

def test_hello(client):
    res = client.get("/")
    assert res.data == b'ok'