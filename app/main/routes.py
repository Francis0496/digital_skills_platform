from datetime import date

from flask import jsonify, render_template
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models import Course, FreelanceOpportunity

from . import bp


@bp.get("/")
def index():
    courses = db.session.scalars(
        db.select(Course)
        .where(Course.is_published.is_(True))
        .order_by(Course.created_at.desc())
        .limit(3)
    ).all()
    opportunities = db.session.scalars(
        db.select(FreelanceOpportunity)
        .where(
            FreelanceOpportunity.status == "active",
            db.or_(
                FreelanceOpportunity.deadline.is_(None),
                FreelanceOpportunity.deadline >= date.today(),
            ),
        )
        .order_by(FreelanceOpportunity.created_at.desc())
        .limit(3)
    ).all()
    return render_template(
        "main/index.html", courses=courses, opportunities=opportunities
    )


@bp.get("/about")
def about():
    return render_template("main/about.html")


@bp.get("/health")
def health():
    """Report whether the web process can reach its configured database."""
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return jsonify(status="unavailable"), 503
    return jsonify(status="ok")
