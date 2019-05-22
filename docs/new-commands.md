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

