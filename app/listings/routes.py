from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Listing, Category, Status
from . import listings_bp


@listings_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    q = Listing.query.order_by(Listing.created_at.desc())
    pagination = q.paginate(page=page, per_page=10, error_out=False)
    listings = pagination.items
    return render_template("listings/index.html", listings=listings, pagination=pagination)

@listings_bp.route('/<int:listing_id>')
def detail(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    return render_template("listings/detail.html", listing=listing)

@listings_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category_id = request.form.get("category_id")
        coordinateX = request.form.get("coordinateX")
        coordinateY = request.form.get("coordinateY")

        if not title or not description or not category_id:
            flash("Моля, попълни всички задължителни полета.")
            return redirect(url_for("listings.create"))
        
        listing = Listing(
            title=title,
            description=description,
            category_id=int(category_id),
            status=Status.LOST,
            coordinateX=float(coordinateX) if coordinateX else None,
            coordinateY=float(coordinateY) if coordinateY else None,
            owner=current_user,
        )
        db.session.add(listing)
        db.session.commit()
        flash("Обявата е създадена успешно!")
        return redirect(url_for("listings.detail", listing_id=listing.id))
    
    categories = Category.query.all()
    return render_template("listings/create.html", categories=categories)
    
@listings_bp.route("/edit/<int:listing_id>", methods=["GET", "POST"])
@login_required
def edit(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    if listing.owner_id != current_user.id and current_user.role.value != "admin":
        abort(403)

    if request.method == "POST":
        listing.title = (request.form.get("title") or "").strip()
        listing.description = (request.form.get("description") or "").strip()
        listing.category_id = request.form.get("category_id", type=int)

        status_val = request.form.get("status", listing.status.value)
        try:
            listing.status = Status(status_val)
        except ValueError:
            flash("Невалиден статус.", "danger")
            return redirect(url_for("listings.edit", listing_id=listing.id))

        print(listing.status)
        listing.coordinateX = request.form.get("coordinateX", type=float)
        listing.coordinateY = request.form.get("coordinateY", type=float)

        db.session.commit()
        flash("Успешно променихте обявата.", "success")
        return redirect(url_for("listings.detail", listing_id=listing.id))  # detail, не details!

    categories = Category.query.all()
    return render_template("listings/edit.html", listing=listing, categories=categories)


@listings_bp.route("/delete/<int:listing_id>", methods=["POST"])
@login_required
def delete(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    if listing.owner_id != current_user.id and getattr(current_user.role, "value", str(current_user.role)) != "admin":
        abort(403)
    db.session.delete(listing)
    db.session.commit()
    flash("Обявата беше изтрита успешно.", "success")
    return redirect(url_for("listings.index"))