from functools import wraps

from flask import abort
from flask_login import current_user


def admin_required(f):
    """Registering the blueprint to check if the user is admin"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or getattr(
                current_user.role, "value", current_user.role) != "admin":
            abort(403)
        return f(*args, **kwargs)

    return wrapper
