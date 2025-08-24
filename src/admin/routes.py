"""Admin dashboard routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.extensions import db

from ..models import Listing, User
from . import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/")
@login_required
@admin_required
def dashboard():
    """Render admin dashboard: overview, users, listings tabs."""
    #Overview she znachi, che tova e default stoinosta, toest ako otvorqt /admin/ she otvori defakto /admin/overview
    tab = request.args.get("tab", "overview")

    total_users = db.session.scalar(select(func.count()).select_from(User))
    total_listings = db.session.scalar(select(func.count()).select_from(Listing))
    by_status = db.session.execute(
        select(Listing.status, func.count(Listing.id)).group_by(Listing.status)
    ).all()
    status_counts = dict(by_status)

    users = []
    listings = []
    if tab == "users":
        users = db.session.execute(
            select(User).order_by(User.created_at.desc())
        ).scalars().all()
    elif tab == "listings":
        listings = db.session.execute(
            select(Listing)
            .options(
                joinedload(Listing.owner),
                joinedload(Listing.category),
                joinedload(Listing.town),
            )
            .order_by(Listing.created_at.desc())
        ).scalars().all()

    return render_template(
        "admin/dashboard.html",
        tab=tab,
        total_users=total_users,
        total_listings=total_listings,
        status_counts=status_counts,
        users=users,
        listings=listings,
    )


@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id: int):
    """Delete a user (and their listings) from the admin panel."""
    user_to_delete = db.session.get(User, user_id)
    if user_to_delete is None:
        flash("Потребителят не е намерен.", "warning")
        return redirect(url_for("admin.dashboard", tab="users"))
    if user_to_delete.id == current_user.id:
        flash("Не можете да изтриете собствения си администраторски акаунт.",
              "danger")
        return redirect(url_for("admin.dashboard", tab="users"))

    db.session.delete(user_to_delete)
    db.session.commit()

    flash(
        f"Потребител '{user_to_delete.email}' и всички негови обяви бяха изтрити.",
        "success")
    return redirect(url_for("admin.dashboard", tab="users"))
