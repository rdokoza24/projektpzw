from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from ..models import User

# Funkcija za provjeru postoji li već takav korisnik/email
def validate_unique_username(form, field):
    if User.get_by_username(field.data):
        raise ValidationError('Korisničko ime je zauzeto.')

def validate_unique_email(form, field):
    if User.get_by_email(field.data):
        raise ValidationError('Email je već registriran.')

class LoginForm(FlaskForm):
    """Forma za prijavu korisnika."""
    username = StringField('Korisničko ime ili Email', validators=[DataRequired()])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    submit = SubmitField('Prijavi se')

class RegistrationForm(FlaskForm):
    """Forma za registraciju novog korisnika."""
    username = StringField('Korisničko ime', validators=[
        DataRequired(), 
        Length(min=4, max=25),
        validate_unique_username # Custom validator
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        validate_unique_email # Custom validator
    ])
    password = PasswordField('Lozinka', validators=[
        DataRequired(), 
        Length(min=6, message='Lozinka mora imati barem 6 znakova.')
    ])
    confirm_password = PasswordField('Ponovi lozinku', validators=[
        DataRequired(), 
        EqualTo('password', message='Lozinke se ne podudaraju.')
    ])
    submit = SubmitField('Registriraj se')