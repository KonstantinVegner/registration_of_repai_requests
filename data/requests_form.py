from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class RequestsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    about = TextAreaField("Текст заявки")
    classroom = TextAreaField("Номер кабинета")
    priority = TextAreaField("Приоритет")
    submit = SubmitField('Отправить')
