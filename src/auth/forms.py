"""Auth forms."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)
from sqlalchemy import select
from ..models import User
from ..extensions import db


class RegistrationForm(FlaskForm):
    """Registration form creation"""
    email = StringField("Имейл:",
                        validators=[DataRequired(),
                                    Email(),
                                    Length(max=100)])

    password = PasswordField(
        "Парола:", validators=[DataRequired(),
                               Length(min=5, max=35)])

    confirm_pass = PasswordField("Потвърди паролата",
                                 validators=[
                                     DataRequired(),
                                     EqualTo("password",
                                             message="Паролите не са еднакви"),
                                     Length(min=5, max=35)
                                 ])

    submit = SubmitField("Регистрирай се")

    def validate_email(self, field):
        existing = db.session.scalar(select(User).where(User.email == field.data))
        if existing:
            raise ValidationError("Този имейл вече е регистриран")


class LoginForm(FlaskForm):
    """Login form creation"""
    email = StringField("Имейл:",
                        validators=[DataRequired(),
                                    Email(),
                                    Length(max=100)])

    password = PasswordField(
        "Парола:", validators=[DataRequired(),
                               Length(min=5, max=35)])

    submit = SubmitField("Вход")
