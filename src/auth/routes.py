from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .. import db
from ..models import Category, Listing, Status, Town, User
from . import bp
from .forms import LoginForm, RegistrationForm


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Успешна регистрация! Моля влезте', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html',
                           title='Регистрация',
                           form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Неправилно потребителско име или парола', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', title='Вход', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    tab = request.args.get("tab", "settings")
    towns = Town.query.order_by(Town.name.asc()).all()
    categories = Category.query.all()
    if request.method == "POST" and tab == "settings":
        town_id = request.form.get("town_id", type=int)
        if town_id:
            town = Town.query.get(town_id)
            if town:
                current_user.town = town

        old = (request.form.get("old_password") or "").strip()
        new = (request.form.get("new_password") or "").strip()
        rep = (request.form.get("repeat_password") or "").strip()

        if old or new or rep:
            if not current_user.check_password(old):
                flash("Невалидна текуща парола.", "danger")
                return redirect(url_for("auth.account", tab="settings"))
            if not new or len(new) < 5:
                flash("Новата парола трябва да е поне 5 символа.", "warning")
                return redirect(url_for("auth.account", tab="settings"))
            if new != rep:
                flash("Паролите не съвпадат.", "warning")
                return redirect(url_for("auth.account", tab="settings"))
            current_user.set_password(new)
            flash("Паролата е сменена.", "success")

        current_user.notify_enabled = bool(request.form.get("notify_enabled"))
        notify_town = request.form.get("notify_town_id", type=int)
        notify_category = request.form.get("notify_category_id", type=int)
        current_user.notify_town_id = notify_town if notify_town and notify_town > 0 else None
        current_user.notify_category_id = notify_category if notify_category and notify_category > 0 else None
        if current_user.notify_town_id == 0:
            current_user.notify_town_id = None
        if current_user.notify_category_id == 0:
            current_user.notify_category_id = None

        db.session.commit()
        flash("Профилът е обновен.", "success")
        return redirect(url_for("auth.account", tab="settings"))

    user_listings_q = Listing.query.filter_by(
        owner_id=current_user.id).order_by(Listing.created_at.desc())
    active_listings = user_listings_q.filter(
        Listing.status != Status.RETURNED).all()
    finished_listings = user_listings_q.filter(
        Listing.status == Status.RETURNED).all()

    return render_template(
        "auth/account.html",
        tab=tab,
        towns=towns,
        active_listings=active_listings,
        finished_listings=finished_listings,
        categories=categories
    )
