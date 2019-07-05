def assert_button_text(data, text):
    assert data["text"] == text, f"button text should be '{text}' but is {data['text']}"


def assert_button_callback_data(data, callback_data):
    assert (
        data["callback_data"] == callback_data
    ), f"button data should be {callback_data} but is {data['callback_data']}"
