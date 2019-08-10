import os
import logging
import flask_injector
from injector import inject

from flask import Flask, g
from pythonjsonlogger import jsonlogger

import tapeworm.providers as providers


class StackDriverJsonFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        log_record["severity"] = log_record["levelname"]
        del log_record["levelname"]
        return super(StackDriverJsonFormatter, self).process_log_record(log_record)


def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    formatter = StackDriverJsonFormatter("(name) (levelname) (message)")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.json_encoder = CustomJSONEncoder
    app.config.from_mapping(
        TOKEN="<default token, override me>",
        WEBHOOK_URL_ID="<default webhook url id, override me>",
        PROJECT_ID="<default project id, override me>",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    if not app.testing:
        setup_logging(logging.DEBUG)

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
        telegram=providers.TelegramClientModule(),
        incoming=providers.IncomingModule(),
        links=providers.LinksClientModule(),
        ds=providers.DatastoreClientModule(),
    )

    flask_injector.FlaskInjector(app=app, modules=injector_default_modules.values())

    return app
