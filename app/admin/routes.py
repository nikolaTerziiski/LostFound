from flask import Blueprint, request, render_template
from . import admin_required
from flask_login import login_required
from ..models import User, Listing
from sqlalchemy.orm import joinedload
from app.extensions import db
from sqlalchemy import func


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
@admin_bp.get("/")
@login_required
@admin_required
def dashboard():
    
    #Overview she znachi, che tova e default stoinosta, toest ako otvorqt /admin/ she otvori defakto /admin/overview
    tab = request.args.get("tab", "overview")

    total_users = User.query.count()
    total_listings = Listing.query.count()
    by_status = (
        db.session.query(Listing.status, func.count(Listing.id))
        .group_by(Listing.status)
        .all()
    )
    status_counts = dict(by_status)

    users = []
    listings = []
    if tab == "users":
        users = User.query.order_by(User.created_at.desc()).all()
    elif tab == "listings":
        listings = (Listing.query
                    .options(joinedload(Listing.owner),
                             joinedload(Listing.category),
                             joinedload(Listing.town))
                    .order_by(Listing.created_at.desc())
                    .all())

    return render_template(
        "admin/dashboard.html",
        tab=tab,
        total_users=total_users,
        total_listings=total_listings,
        status_counts=status_counts,
        users=users,
        listings=listings,
    )
    
    