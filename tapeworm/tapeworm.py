import logging
import json
import requests

from flask import Blueprint, request, current_app, g
from pathlib import Path

from .message_handler import handle_message, handle_callback_query

logger = logging.getLogger(__name__)

bp = Blueprint('telegram', __name__)

@bp.route('/me', methods=['GET'])
def me():
    return proxy_request_as_flask_response(current_app.config['TG_URL'] + 'getMe')

def as_json(payload):
    return current_app.response_class(
        response=json.dumps(payload),
        status=200,
        mimetype='application/json'
    )

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
        return False, {
            'payload': payload,
            'status_code': res.status_code,
            'response': json.loads(res.text)
        }
    return True, None

def editMessageText(config, payload):
    res = requests.post(config['TG_URL'] + 'editMessageText', data=payload)
    if res.status_code != requests.codes.ok:
        return False, {
            'payload': payload,
            'status_code': res.status_code,
            'response': json.loads(res.text)
        }
    return True, None

def answerCallbackQuery(config, payload):
    res = requests.post(config['TG_URL'] + 'answerCallbackQuery', data=payload)
    if res.status_code != requests.codes.ok:
        return False, {
            'payload': payload,
            'status_code': res.status_code,
            'response': json.loads(res.text)
        }
    return True, None

def send_response(payload, response_fn):
    if payload is None:
        return "ok"

    logger.debug(payload)
    ok, err = response_fn(current_app.config, payload)

    if not ok and current_app.config['DEBUG']:
        return as_json(err)
    if not ok:
        logger.error(err)
        return "ok"

    if current_app.config['DEBUG']:
        return as_json(payload)
    return "ok"

@bp.route('/webhook_<url_id>', methods=['POST'])
def webhook_message(url_id):
    if url_id != current_app.config['WEBHOOK_URL_ID']:
        return "ok"

    logger.debug(f"Request from {request.remote_addr}")
    body = json.loads(request.data)
    logger.debug(body)
    if 'message' in body:
        res = handle_message(body['message'])
        return send_response(res, sendMessage)
    elif 'callback_query' in body:
        answer_query_res = send_response(
            {'callback_query_id': body['callback_query']['id']},
            answerCallbackQuery)

        res = handle_callback_query(body['callback_query'])
        callback_query_res = send_response(res, editMessageText)
        if current_app.config['DEBUG']:
            return as_json({
                'answer_query': answer_query_res.get_json(),
                'callback_query': callback_query_res.get_json()
            })
    return "ok"