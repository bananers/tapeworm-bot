import logging
import urllib
import json
import os
import requests
import configparser

from flask import Blueprint, request
from pathlib import Path

from .message_handler import handle_message
from .utils import parse_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bp = Blueprint('telegram', __name__)

@bp.route('/')
def index():
    return 'ok'

app = Flask(__name__)

BASE_URL = "https://api.telegram.org/bot"
config = parse_config(BASE_URL)

def proxy_request_as_flask_response(url, params={}):
    res = requests.get(url, params=params)
    return app.response_class(
        response=res.text,
        status=200,
        mimetype='application/json'
    )

@app.route("/", methods=['GET'])
def index():
    return "ok"

@app.route('/me', methods=['GET'])
def me():
    return proxy_request_as_flask_response(config['telegram_url'] + 'getMe')

@app.route('/info_webhook', methods=['GET'])    
def get_webhook_info():
    return proxy_request_as_flask_response(config['telegram_url'] + 'getWebhookInfo')

@app.route('/updates', methods=['GET'])
def get_latest_messages():
    offset = request.args.get('offset', 0)
    return proxy_request_as_flask_response(
        config['telegram_url'] + 'getUpdates',
        {'offset': offset})

@app.route('/webhook', methods=['POST', 'DELETE'])
def webhook_settings():
    if request.method == 'POST':
        logger.info('Setting webhook')
        hook_url = f"https://{config['project_id']}.appspot.com/webhook_{config['webhook_url_id']}"

        url = config['telegram_url'] + "setWebhook"
        return proxy_request_as_flask_response(url, {
            'url': hook_url,
            'max_connections': 2,
            'allowed_updates': ['message']
        })
    elif request.method == 'DELETE':
        url = config['telegram_url'] + "deleteWebhook"
        return proxy_request_as_flask_response(url)    
    else:
        return "ok"

def sendMessage(config, payload):
    res = requests.post(config['telegram_url'] + 'sendMessage', data=payload)
    if res.status_code != requests.codes.ok:
        logger.error(f'Failed to send message payload={payload}')

@app.route('/webhook_' + config['webhook_url_id'], methods=['POST'])
def webhook_message():
    logger.debug(f"Request from {request.remote_addr}")
    body = json.loads(request.data)
    logger.debug(body)
    if 'message' in body:
        res = handle_message(body['message'])
        if res is not None:
            logger.debug(res)
            sendMessage(config, res)

    return "ok"