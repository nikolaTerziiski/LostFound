from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import MultipleFileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    text = TextAreaField("Коментар",
                         validators=[
                             DataRequired(message="Моля, напишете коментар."),
                             Length(max=2000)
                         ])
    images = MultipleFileField(
        "Снимки",
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'],
                        'Снимките трябва да са във формат: JPG/PNG/WebP')
        ])
    submit = SubmitField("Напиши")
