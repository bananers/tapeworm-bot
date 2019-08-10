# pylint: disable=no-member

import logging
import json
import requests
from injector import inject
from flask import Blueprint, request, current_app, render_template

from tapeworm.incoming import Incoming
from tapeworm.model_link import Links

logger = logging.getLogger(__name__)

bp = Blueprint("telegram", __name__)

# pylint: disable=invalid-name
@bp.route("/me", methods=["GET"])
def me():
    return proxy_request_as_flask_response(current_app.config["TG_URL"] + "getMe")


def as_json(payload):
    return current_app.response_class(
        response=json.dumps(payload), status=200, mimetype="application/json"
    )


def proxy_request_as_flask_response(url, params=None):
    res = requests.get(url, params=params if params is not None else {})
    return current_app.response_class(
        response=res.text, status=200, mimetype="application/json"
    )


@bp.route("/info_webhook", methods=["GET"])
def get_webhook_info():
    return proxy_request_as_flask_response(
        current_app.config["TG_URL"] + "getWebhookInfo"
    )


@bp.route("/updates", methods=["GET"])
def get_latest_messages():
    offset = request.args.get("offset", 0)
    return proxy_request_as_flask_response(
        current_app.config["TG_URL"] + "getUpdates", {"offset": offset}
    )


@bp.route("/webhook", methods=["POST", "DELETE"])
def webhook_settings():
    if request.method == "POST":
        logger.info("Setting webhook")
        # pylint: disable=line-too-long
        hook_url = f"https://{current_app.config['PROJECT_ID']}.appspot.com/webhook_{current_app.config['WEBHOOK_URL_ID']}"

        url = current_app.config["TG_URL"] + "setWebhook"
        return proxy_request_as_flask_response(
            url, {"url": hook_url, "max_connections": 2, "allowed_updates": ["message"]}
        )

    if request.method == "DELETE":
        url = current_app.config["TG_URL"] + "deleteWebhook"
        return proxy_request_as_flask_response(url)
    return "ok"


@inject
@bp.route("/webhook_<url_id>", methods=["POST"])
def webhook_message(url_id, incoming: Incoming):
    if url_id != current_app.config["WEBHOOK_URL_ID"]:
        return "ok"

    try:
        body = json.loads(request.data)
        logger.debug(
            "Received request from", extra={"addr": request.remote_addr, "body": body}
        )
        return as_json(incoming.handle_data(body))
    except Exception:  # pylint: disable=broad-except
        logger.exception("ignoring message due to exception", extra={"body": body})
        return "ok"


@bp.route("/links", methods=["GET"])
def view_html(links: Links):
    offset_str = request.args.get("offset", "0")
    offset = int(offset_str) if offset_str.isdigit() else 0
    if offset <= 0:
        offset = 0
    amount_per_page = 50
    available_to_go_back = min(offset, amount_per_page)
    return render_template(
        "links.html",
        endpoint="/links",
        links=links.list_links(offset, amount_per_page),
        offset=offset,
        amount_per_page=amount_per_page,
        available_to_go_back=available_to_go_back,
    )
