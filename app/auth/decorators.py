from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def roles_required(*role_names):
    """Require authentication and membership of one approved role."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_active or current_user.role_name not in role_names:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
