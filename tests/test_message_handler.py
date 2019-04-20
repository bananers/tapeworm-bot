from context import tapeworm
import tapeworm.message_handler as mh


def test_help_response():
    assert mh.handle_message({
        'chat': {
            'id': -1
        },
        'text': '/help'
    }) is not None