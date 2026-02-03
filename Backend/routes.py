from flask import Blueprint, jsonify

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})
