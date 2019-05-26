This document introduces command parsing and returning responses back to the user. We'll be adding a simple ping/pong response for the bot as a way to check whether the bot is alive.

# Creating a command

In `tapeworm/message_handler.py`, add a command in this case `/ping` inside of the `handle_message`. You can parse for commands via the `is_command_of` function that returns whether the text is a command or not like so:

```py
if is_command_of(text, "ping"):
    # You can do whatever you want here, we are just returning a pong message
    return response_text(message, "pong")
```

# Response to Telegram

Since the ping/pong combo simply returns text, we can use the `response_text` method which builds a response via the source message. This sends a response back to Telegram to send the "pong" method back to the same chat group [more info](https://core.telegram.org/bots/api#sendmessage).

# Writing tests to the new command

Since the message handler does not depend on any external dependencies outside of writing to the datastore for specific cases, we can easily unit test the implementation by simulating the structure that Telegram message objects and importing the message handler directly like so:

```py
# PS: This function already exists in test_message_handler.py
def _create_text_message(text):
    return {"chat": {"id": -1}, "text": text}

# and for the associated test
def test_ping_response():
    res = message_handler.handle_message(_create_text_message("/ping"))
    assert res is not None
    assert res['text'] == "pong"
```

# Storing data

This project uses Google Cloud Datastore as a backing database. Since we don't have access to the datastore in development, you will have to emulate a local datastore before this can work. More information can be found in the main README.

The various CRUD methods can be found in `tapeworm/model_link.py`. Here is a summary on how you can add a new link to the database:

## Writing data
```py
# First, create an instance of a Link object via the from_dict method

from model_link import from_dict, create
from datetime import datetime
today = datetime.utcnow()

# In this case, 12312312 is a telegram user ID
link = from_dict({
    'link': 'http://example.com',
    'title': 'Example',
    'by': '12312312',
    'date': today
})

created_link = create(link)
```

## Listing data

```py
# The list_link method returns the last 10 links added

from model_link import list_links

links = list_links()
```