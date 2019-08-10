import logging

from flask import Blueprint, jsonify
import tapeworm.model_link as model_link

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/links", methods=["GET"])
def all_links(links: model_link.Links):
    return jsonify([x._asdict() for x in links.list_links()])
