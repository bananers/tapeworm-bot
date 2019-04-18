tapeworm is a telegram bot that sits in a chat group silently gobbling up interesting information on the chat group. This application runs on AppEngine.

# Requirements

Before you can start, you will need to create a sandbox constraining the version to python 3.7 since this runs on AppEngine. Shown below is an example of creating an environment constrained to Python 3.7.

`conda create -n environment-name python=3.7`

# Dependencies

This project uses a requirement.txt to store dependencies since AppEngine doesn't support the new Pipfile format. Shown below is the command you can use.

`pip install -r requirements.txt`

# Starting development

Since this bot uses Cloud Datastore, you'll have to run an emulator to simulate the database insertions. Otherwise, you'll not be able to test anything that has to do with a database [more info](https://cloud.google.com/datastore/docs/tools/datastore-emulator).

**TL;DR**

1. `gcloud components install cloud-datastore-emulator`
2. `gcloud components install beta`
3. `gcloud beta emulators datastore start`

You'll then need to expose the environment variables to get the library to talk to the local datastore.

This sets up your environment variables for local dev

`gcloud beta emulators datastore env-init > set_vars.cmd && set_vars.cmd`

## Configuration

With that in place, you should then copy the provided `config-example.ini` to `config.ini` and replace the variables as necessary.

The `bot` variable is simply the token that BotFather provides to you when registering the bot.
The `webhook_url_id` variable is simply a random string that the telegram calls to send new messages to. The reason for this variable is to prevent external parties (not Telegram) from calling the API with rubbish values. Although, an IP whitelist should preferably be added either on GAE or in the source code itself.
The `project_id` variable is used when setting webhooks since we need a webhook endpoint for Telegram to call when setting the webhook. See the /webhook endpoint for more details in the code.

If you're developing this only locally, you should not need the two latter variables since they are only used for setting up the webhook details.

## Simple logic extensions

In the case where you want to develop extensions for purely logic IE: you only need the database and are not sending anything back to the messenger. You should be fine with just writing tests on the functions on `message_handler.py` as the functions pertaining to string handling are mostly pure except for the functions that need more details. There is a simple test written for the `/help` command that simply asserts that the response is not None.

## More complicated changes

In the case where you want to develop more complicated workflows like a back and forth game with the bot, you'll probably need to register a new token that doesn't interefere with the existing bot running in production. **TODO** See issue #1