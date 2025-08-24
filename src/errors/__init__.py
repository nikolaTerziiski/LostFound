"""Error handlers."""

from flask import Blueprint, render_template

errors_bp = Blueprint("errors", __name__, template_folder="templates")

@errors_bp.app_errorhandler(404)
def not_found(error):
    """Return 404 page."""
    return render_template("errors/404.html"), 404

@errors_bp.app_errorhandler(403)
def forbidden(error):
    """Return 403 page. No access"""
    return render_template("errors/403.html"), 403
