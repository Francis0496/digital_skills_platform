from flask import Blueprint

bp = Blueprint("mentorship", __name__, url_prefix="/mentorship")

from . import routes  # noqa: E402, F401
