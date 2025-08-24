from flask import Blueprint, render_template
from ..models import Listing


bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('home.html')