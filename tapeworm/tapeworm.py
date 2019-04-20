import logging
import json
import requests

from flask import Blueprint, request, current_app, g
from pathlib import Path

from .message_handler import handle_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bp = Blueprint('telegram', __name__)

@bp.route('/me', methods=['GET'])
def me():
    return proxy_request_as_flask_response(current_app.config['TG_URL'] + 'getMe')

def proxy_request_as_flask_response(url, params={}):
    res = requests.get(url, params=params)
    return current_app.response_class(
        response=res.text,
        status=200,
        mimetype='application/json'
    )

@bp.route('/info_webhook', methods=['GET'])
def get_webhook_info():
    return proxy_request_as_flask_response(current_app.config['TG_URL'] + 'getWebhookInfo')

@bp.route('/updates', methods=['GET'])
def get_latest_messages():
    offset = request.args.get('offset', 0)
    return proxy_request_as_flask_response(
        current_app.config['TG_URL'] + 'getUpdates',
        {'offset': offset})

@bp.route('/webhook', methods=['POST', 'DELETE'])
def webhook_settings():
    if request.method == 'POST':
        logger.info('Setting webhook')
        hook_url = f"https://{current_app.config['PROJECT_ID']}.appspot.com/webhook_{current_app.config['WEBHOOK_URL_ID']}"

        url = current_app.config['TG_URL'] + "setWebhook"
        return proxy_request_as_flask_response(url, {
            'url': hook_url,
            'max_connections': 2,
            'allowed_updates': ['message']
        })
    elif request.method == 'DELETE':
        url = current_app.config['TG_URL'] + "deleteWebhook"
        return proxy_request_as_flask_response(url)
    else:
        return "ok"

def sendMessage(config, payload):
    res = requests.post(config['TG_URL'] + 'sendMessage', data=payload)
    if res.status_code != requests.codes.ok:
        logger.error(f'Failed to send message payload={payload}')

@bp.route('/webhook_<url_id>', methods=['POST'])
def webhook_message(url_id):
    if url_id != current_app.config['WEBHOOK_URL_ID']:
        return "ok"

    logger.debug(f"Request from {request.remote_addr}")
    body = json.loads(request.data)
    logger.debug(body)
    if 'message' in body:
        res = handle_message(body['message'])
        if res is not None:
            logger.debug(res)
            sendMessage(current_app.config, res)

    return "ok"