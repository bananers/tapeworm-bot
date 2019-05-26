import tapeworm.message_handler as mh


def _create_text_message(text):
    return {"chat": {"id": -1}, "text": text}


def test_help_response():
    assert mh.handle_message(_create_text_message("/help")) is not None


def test_ping_response():
    res = mh.handle_message(_create_text_message("/ping"))
    assert res is not None
    assert res["text"] == "pong"
