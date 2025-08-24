"""Defining the main route (INDEX PAGE)"""

from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Initiallizing the main page"""
    return render_template('home.html')
