from context import tapeworm
import tapeworm.message_handler as mh

def _create_text_message(text):
    return {
        'chat': {
            'id': -1
        },
        'text': text
    }
def test_help_response():
    assert mh.handle_message(_create_text_message('/help')) is not None