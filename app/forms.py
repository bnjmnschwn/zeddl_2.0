from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SpaceForm(FlaskForm):
    spacename = StringField('Spacename', validators=[DataRequired()])
    submit = SubmitField('Create Space')
