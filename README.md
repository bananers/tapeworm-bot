tapeworm is a telegram bot that sits in a chat group silently gobbling up interesting information on the chat group. This application runs on AppEngine.

# Requirements

Before you can start, you will need to create a sandbox constraining the version to python 3.7 since this runs on AppEngine. Shown below is an example of creating an environment constrained to Python 3.7.

`conda create -n environment-name python=3.7`

# Dependencies

This project uses a requirement.txt to store dependencies since AppEngine doesn't support the new Pipfile format. Shown below is the command you can use.

`pip install -r requirements/requirements-dev.txt`

# Emulators

Since this bot uses Cloud Datastore, you'll have to run an emulator to simulate the database insertions. Otherwise, you'll not be able to test anything that has to do with a database [more info](https://cloud.google.com/datastore/docs/tools/datastore-emulator).

**TL;DR**

1. `gcloud components install cloud-datastore-emulator`
2. `gcloud components install beta`
3. `gcloud beta emulators datastore start`

You'll then need to expose the environment variables to get the library to talk to the local datastore.

This sets up your environment variables for local dev

`gcloud beta emulators datastore env-init > set_vars.cmd && set_vars.cmd`

# Developing

## Configuration

This project follows the Flask method for [instance folders](http://flask.pocoo.org/docs/1.0/config/#instance-folders) so you should create an instance folder in the project root and copy `config-example.py` into `instance/config.py` replacing the variables as necessary.

The `bot` variable is the token that BotFather provided when registering the bot.

The `webhook_url_id` variable is a random string that Telegram calls when it receives new messages. The reason for this variable is to prevent external parties (not Telegram) from calling the API with rubbish values. However, an IP whitelist should be preferred atop of this.

The `project_id` variable is used to create the webhook URL that Telegram would call and since this project runs on AppEngine, the base URL used for assembling the webhook URL is `https://project_id.appspot.com`

The two latter variables are only applicable when the program is run in AppEngine since it doesn't apply when you are developing locally since Telegram requires a HTTPS endpoint and a public domain for webhook URLs.

Now that you have the prerequisite tooling installed, you can get started by viewing the [docs folder](https://github.com/bananers/tapeworm-bot/tree/master/docs)