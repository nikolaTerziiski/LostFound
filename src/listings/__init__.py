#listings/__init__.py
from flask import Blueprint

listings_bp = Blueprint('listings', __name__, template_folder='templates', url_prefix='/listings')

from . import routes
