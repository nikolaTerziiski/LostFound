from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from ..models import User


class RegistrationForm(FlaskForm):
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
        if any(User.query.filter_by(email=field.data)):
            raise ValidationError("Този имейл вече е регистриран")


class LoginForm(FlaskForm):
    email = StringField("Имейл:",
                        validators=[DataRequired(),
                                    Email(),
                                    Length(max=100)])

    password = PasswordField(
        "Парола:", validators=[DataRequired(),
                               Length(min=5, max=35)])

    submit = SubmitField("Вход")
