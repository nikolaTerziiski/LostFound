from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    text = TextAreaField(
        "Коментар",
        validators=[DataRequired(message="Моля, напишете коментар."), Length(max=2000)]
    )
    submit = SubmitField("Напиши")
