from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, EmailField, BooleanField, \
SubmitField, TextAreaField
from wtforms.validators import DataRequired

class login_form(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class contact_form(FlaskForm):
    name = StringField(label="name", validators=[DataRequired()])
    email = EmailField(label="email", validators=[DataRequired()])
    subject = StringField(label="subject", validators=[DataRequired()])
    message = TextAreaField(label="message", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Send Message")