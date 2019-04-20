import os

from flask import Flask, g

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        TOKEN='<default token, override me>',
        WEBHOOK_URL_ID='<default webhook url id, override me>',
        PROJECT_ID='<default project id, override me>'
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    app.config.update(TG_URL="https://api.telegram.org/bot" + app.config['TOKEN'] + '/')
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        return 'ok'

    from tapeworm import tapeworm
    app.register_blueprint(tapeworm.bp)

    return app