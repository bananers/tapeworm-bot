import logging

from flask import Blueprint, jsonify, request
import tapeworm.model_link as model_link

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__, url_prefix="/api")


def is_number(source, default_value=0) -> (int, bool):
    try:
        return (int(source), True)
    except ValueError:
        return (default_value, False)


def is_non_negative(number) -> bool:
    return number >= 0


def error_response(message):
    return jsonify({"error": message, "results": []})


@bp.route("/links", methods=["GET"])
def all_links(links: model_link.Links):
    limit: str = request.args.get("limit", "10") or "10"
    offset: str = request.args.get("offset", "0") or "0"

    limit, ok = is_number(limit, 10)
    if not ok:
        return error_response("limit is not a number")

    if not is_non_negative(limit):
        return error_response("limit cannot be negative")

    offset, ok = is_number(offset, 0)
    if not ok:
        return error_response("offset is not a number")

    if not is_non_negative(offset):
        return error_response("offset cannot be negative")

    return jsonify(
        {"results": [x._asdict() for x in links.list_links(limit=limit, offset=offset)]}
    )


@bp.route("/ping", methods=["GET"])
def ping():
    return "pong"
