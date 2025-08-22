# # app/admin/__init__.py
# from flask import Blueprint, abort
# from flask_login import current_user
# from functools import wraps
# from ..models import Role

# admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# def admin_required(view):
#     @wraps(view)
#     def wrapped(*args, **kwargs):
#         if not current_user.is_authenticated:
#             # Flask-Login ще те пренасочи към login_view, ако закачиш @login_required
#             abort(403)
#         # ролята ти е Enum(Role); ползвай .value == "admin"
#         if getattr(current_user, "role", None) != Role.ADMIN:
#             abort(403)
#         return view(*args, **kwargs)
#     return wrapped
