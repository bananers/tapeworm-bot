tapeworm is a telegram bot that sits in a chat group silently gobbling up interesting information on the chat group built with AppEngine and DataStore.

# Requirements

You'll need to create a virtualenv based on Python 3.7

1. `conda create -n environment-name python=3.7`
2. `pip install -r requirements/dev.txt`

# Developing

You'll need the following in `instance/config.py`:

1. `TOKEN` A Telegram API token [details here](https://core.telegram.org/bots#6-botfather)
2. `WEBHOOK_URL_ID` A random string of characters
3. `PROJECT_ID` Which is the associated Google Cloud project id

Example:

```py
TOKEN = "<your token>"
WEBHOOK_URL_ID = "22222"
PROJECT_ID = "<your project id>"
```

# Running the bot

For the API server

`nox -s run`

For the frontend server

`cd app && npm start`

The API server will be running on http://localhost:8080, UI will be accessible via http://localhost:3000