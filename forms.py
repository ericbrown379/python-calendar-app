from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp, Email
from email_manager import check_email_exists
from models import User
# Custom validator to check for forbidden characters
def check_forbidden_characters(form, field):
    """Checks password forbidden characters"""
    forbidden_characters = set("#$%^&*(){}[]<>?")
    if any(char in forbidden_characters for char in field.data):
        raise ValidationError("Password contains forbidden characters.")

def email_exists(form, field):
    """Utilizes the email checks from email_manager for validation in the email form field"""
    if not check_email_exists(field.data):
        print("This email does not exist.")
        raise ValidationError("This email does not exist.")
    email_address = field.data 
    if User.query.filter_by(email=email_address).first(): 
        raise ValidationError("This email is already registered.")

def email_exists_in_db(form, field):
    """Utilizes the email checks from email_manager for validation in the email form field"""
    email_address = field.data 
    if not User.query.filter_by(email=email_address).first(): 
        raise ValidationError("This email is already registered.")  
def user_exists(form, field):
    """Does a simple query in the User model to check if the username already exists in the DB"""
    inputusername = field.data
    # Check if the username already exists in the database
    if User.query.filter_by(username=inputusername).first() is not None:
        raise ValidationError("This username is taken.")

def user_does_not_exist(form, field):
    """Checks if the username doesn't exist in the user model"""
    inputusername = field.data
    # Check if the username does not exist in the database
    if User.query.filter_by(username=inputusername).first() is None:
        raise ValidationError("This username does not exist.")
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), user_does_not_exist])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message="Email not valid"), email_exists #Makes sure they entered an email
        ]
    )
    username = StringField('Username', validators=[DataRequired(), user_exists])
    # Add a regex to ensure one special character (excluding forbidden ones)
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(),
            # Ensure at least one special character
            Regexp(r'^(?=.*[!@#$%^&+=])', message="Password must contain at least one special character (!, @, #, etc.)"),
            # Ensure no forbidden characters are used
            check_forbidden_characters
        ]
    )
    
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message="Email not valid"), email_exists_in_db #Makes sure they entered an email
        ]
    )
    submit = SubmitField('Submit')


class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Submit')