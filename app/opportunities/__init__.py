from flask import Blueprint

bp = Blueprint("opportunities", __name__, url_prefix="/opportunities")

from . import routes  # noqa: E402, F401
