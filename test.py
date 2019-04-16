import pytest

from message_handler import handle_message

def test_help():
    assert handle_message({ 
        'chat': {"id": -1}, 
        'text': '/help'}) is not None