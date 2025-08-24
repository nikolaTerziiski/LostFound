"""Registering the listing blueprint"""

#listings/__init__.py
from . import routes
from flask import Blueprint

listings_bp = Blueprint('listings', __name__, template_folder='templates', url_prefix='/listings')

