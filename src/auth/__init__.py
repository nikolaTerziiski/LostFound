"""Initialize the auth blueprint"""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from . import routes
