from flask import Blueprint

bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")

from . import routes  # noqa: E402, F401
