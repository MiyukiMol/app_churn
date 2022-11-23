from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length

# create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField()


# create a Form class
class UserForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired()])
    username = StringField("username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField('confirm password', validators=[DataRequired()])
    submit = SubmitField("S'inscrire")