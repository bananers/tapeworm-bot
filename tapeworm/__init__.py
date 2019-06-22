import os
import flask_injector
from injector import inject

from flask import Flask, g

import tapeworm.providers as providers
import tapeworm.ext.telegram as tg
from tapeworm.incoming import Incoming


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        TOKEN="<default token, override me>",
        WEBHOOK_URL_ID="<default webhook url id, override me>",
        PROJECT_ID="<default project id, override me>",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    app.config.update(TG_URL="https://api.telegram.org/bot" + app.config["TOKEN"] + "/")
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # pylint: disable=unused-variable
    @app.route("/")
    def hello():
        return "ok"

    from tapeworm import tapeworm

    app.register_blueprint(tapeworm.bp)

    injector_default_modules = dict(
        telegram=providers.TelegramClientModule(), incoming=providers.IncomingModule()
    )

    flask_injector.FlaskInjector(app=app, modules=injector_default_modules.values())

    return app
