from flask import jsonify, render_template
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db

from . import bp


@bp.get("/")
def index():
    return render_template("main/index.html")


@bp.get("/health")
def health():
    """Report whether the web process can reach its configured database."""
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return jsonify(status="unavailable"), 503
    return jsonify(status="ok")
