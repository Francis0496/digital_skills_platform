from flask import Blueprint

bp = Blueprint("courses", __name__, url_prefix="/courses")

from . import routes  # noqa: E402, F401
