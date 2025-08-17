from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import bp
from .. import db
from ..models import User
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
        flash('Успешна регистрация! Моля влезте','success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Регистрация', form=form)


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
def logout():
    logout_user()
    return redirect(url_for('main.index'))