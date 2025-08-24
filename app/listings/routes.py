from flask import render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Listing, Category, Status, ListingImage, Comment, Town, CommentImage, CommentStatus
from . import listings_bp
from sqlalchemy import or_, func
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
from .forms import CommentForm
import secrets
import os
from .notifications import notify_all_users

def save_image(form_image):
    hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = hex + f_ext
    image_path = os.path.join(current_app.root_path, '..', current_app.config['UPLOAD_PICTURES'], image_fn)

    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    i = Image.open(form_image)
    width, height = i.size
    
    new_width = 500
    new_height = int(new_width * height / width)
    i = i.resize((new_width, new_height), Image.Resampling.LANCZOS)
    i.save(image_path)
    return image_fn

@listings_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    
    search_query = request.args.get('q', '').strip()
    category_input = request.args.get('category', type=int)
    town = request.args.get('town', type=int)
    
    query = Listing.query.order_by(Listing.created_at.desc())
    categories = Category.query.order_by(Category.name.asc())
    
    
    if(search_query):
        query = query.filter(or_(
            Listing.title.ilike(f"%{search_query}%")),
            Listing.description.lower().ilike(f"%{search_query}%"))
        
    if (category_input):
        query = query.filter_by(category_id=category_input)
    
    if (town):
        query = query.filter(Listing.town_id == town)
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    towns = Town.query.order_by(Town.name.asc()).all()
    listings = pagination.items
    
    return render_template("listings/index.html", listings=listings, pagination=pagination, search_query=search_query, categories=categories, towns=towns, category_id=category_input, town=town)

@listings_bp.route('/<int:listing_id>', methods=["GET", "POST"])
def detail(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    
    print(listing.status)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            abort(403)
        
        comment = Comment(
            text=comment_form.text.data.strip(),
            listing_id=listing.id,
            commenter_id=current_user.id
        )
        
        db.session.add(comment)
        db.session.flush()
        
        if len(comment_form.images.data) > 0:
            for file in comment_form.images.data:
                filename = save_image(file)
                db.session.add(CommentImage(image_path=filename, comment_id=comment.id))
        
        db.session.commit()
        flash("Успешно оставихте коментар!", "success")
        return redirect(url_for("listings.detail", listing_id=listing.id))
    
    
    if request.method == "POST" and not comment_form.validate():
        flash("Моля, напишете нещо във формата!.", "danger")
    
    listings_comment = (Comment.query.filter_by(listing_id=listing.id).order_by(Comment.created_at.asc()).all())
    return render_template("listings/detail.html", listing=listing, form=comment_form, comments=listings_comment)

@listings_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        category_id = request.form.get("category_id")
        coordinateX = request.form.get("coordinateX")
        coordinateY = request.form.get("coordinateY")
        date_event_str = request.form.get("date_event")
        contact_name = request.form.get("contact_name")
        contact_phone = request.form.get("contact_phone")
        contact_email = request.form.get("contact_email")
        town_id = request.form.get("town_id", type=int)
        
        if not title or not description or not category_id:
            flash("Моля, попълни всички задължителни полета.")
            return redirect(url_for("listings.create"))
        
        image_files = request.files.getlist('images')
        image_filename = None    
        
        if not Category.query.get(category_id) or not Town.query.get(town_id):
            flash("Невалидна категория или град.", "danger")
            return redirect(url_for("listings.create"))
        
        date_event_obj = datetime.strptime(date_event_str, '%Y-%m-%d').date()
        
        listing = Listing(
            title=title,
            description=description,
            category_id=int(category_id),
            status=Status.LOST,
            coordinateX=float(coordinateX) if coordinateX else None,
            coordinateY=float(coordinateY) if coordinateY else None,
            owner=current_user,
            date_event=date_event_obj,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            town_id = town_id
        )
        
        for image_file in image_files:
            if image_file and image_file.filename != '':
                image_filename = save_image(image_file)
                new_image = ListingImage(image_path=image_filename, listing=listing)
                db.session.add(new_image)
        
        db.session.add(listing)
        db.session.commit()
        notify_all_users(listing=listing)
        flash("Обявата е създадена успешно!", "success")
        return redirect(url_for("listings.detail", listing_id=listing.id))
    
    categories = Category.query.all()
    towns = Town.query.all()
    return render_template("listings/create.html", categories=categories, towns=towns)
    
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

        listing.contact_name = request.form.get("contact_name")
        listing.contact_phone = request.form.get("contact_phone")
        listing.contact_email = request.form.get("contact_email")
        
        date_event_str = request.form.get("date_event")
        if date_event_str:
            listing.date_event = datetime.strptime(date_event_str, '%Y-%m-%d').date()
        
        status_val = request.form.get("status", listing.status.value)
        try:
            listing.status = Status(status_val)
        except ValueError:
            flash("Невалиден статус.", "danger")
            return redirect(url_for("listings.edit", listing_id=listing.id))

        image_file = request.files.get('image')
        image_filename = None
        
        if image_file and image_file.filename != '':
            image_filename = save_image(image_file)
            
        listing.coordinateX = request.form.get("coordinateX", type=float)
        listing.coordinateY = request.form.get("coordinateY", type=float)

        db.session.commit()
        flash("Успешно променихте обявата.", "success")
        return redirect(url_for("listings.detail", listing_id=listing.id))  # detail, не details!

    categories = Category.query.all()
    return render_template("listings/edit.html", listing=listing, categories=categories, status=Status)


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


@listings_bp.route("/map", methods=["GET"])
def map():
    listings = Listing.query.filter(Listing.status != Status.RETURNED).all()
    
    return render_template("listings/map.html", listings=listings)

@listings_bp.route("/<int:listing_id>/returned", methods=["POST"])
def returned(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    if not (current_user.is_authenticated and listing.owner_id == current_user.id):
        abort(403)
        
    listing.status = Status.RETURNED
    db.session.commit()
    flash("Обявата е отбелязана като НАМЕРЕНА - ЧЕСТИТО!!.", "success")
    return redirect(url_for("listings.detail", listing_id=listing.id))

#HERE I MAKE THE COMMENTS ROUTES - SINCE THEY ARE DIRECTLY CONNECTED TO THE
#LISTINGS THERE IS NO NEED IN SEPARATE MODULE BUT IT'S RECOMMENDED
@login_required
@listings_bp.route("/comment/<int:listing_id>/<int:comment_id>", methods=["POST"])
def delete_comment(listing_id: int, comment_id: int):
    listing = Listing.query.get_or_404(listing_id)
    comment = Comment.query.get_or_404(comment_id)
    
    is_admin = getattr(current_user.role, "value", current_user.role) == "admin"
    is_owner_of_listing = listing.owner_id == current_user.id
    is_owner_of_comment = comment.commenter_id == current_user.id
    
    if not (is_admin or is_owner_of_listing or is_owner_of_comment):
        abort(403)
    
    
    db.session.delete(comment)
    db.session.commit()
    flash("Коментарът е изтрит.", "success")
    return redirect(url_for("listings.detail", listing_id=listing.id))


@login_required
@listings_bp.post("/comment/<int:listing_id>/<int:comment_id>/accept")
def accept_comment(listing_id: int, comment_id: int):

    comment = Comment.query.get_or_404(comment_id)
    listing = Listing.query.get_or_404(listing_id)
    
    if not (current_user.is_authenticated and listing.owner_id == current_user.id):
        abort(403)
        
    if comment.status == CommentStatus.PENDING:
        comment.status = CommentStatus.CONFIRMED
        listing.status = Status.FOUND
        db.session.commit()
        flash("Вашата вещ е успешно намерена!", "success")
    
    return redirect(url_for("listings.detail", listing_id=listing_id))

@listings_bp.post("/listing/<int:listing_id>/comment/<int:comment_id>/reject")
@login_required
def reject_comment(listing_id: int, comment_id: int):
    listing = Listing.query.get_or_404(listing_id)
    comment = Comment.query.get_or_404(comment_id)

    if not (current_user.is_authenticated and listing.owner_id == current_user.id):
        abort(403)

    if comment.status == CommentStatus.PENDING:
        comment.status = CommentStatus.REJECTED
        db.session.commit()
        flash("Коментарът е отбелязан като „Не е това“.", "info")

    return redirect(url_for("listings.detail", listing_id=listing.id))
    