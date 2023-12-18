from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SpaceForm(FlaskForm):
    spacename = StringField('Gib deinem Einkaufszeddl einen Namen', validators=[DataRequired()])
    submit = SubmitField('Los gehts!')
