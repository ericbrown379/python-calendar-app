from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, TimeField, SelectField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp, Email, EqualTo
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
    if User.query.filter_by(email=email_address).first() is None: 
        raise ValidationError("This email doesn't exist")  
    
def user_exists(form, field):
    """Does a simple query in the User model to check if the username already exists in the DB"""
    inputusername = field.data
    if User.query.filter_by(username=inputusername).first() is not None:
        raise ValidationError("This username is taken.")

def user_does_not_exist(form, field):
    """Checks if the username doesn't exist in the user model"""
    inputusername = field.data
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
            Email(message="Email not valid"), email_exists 
        ]
    )
    username = StringField('Username', validators=[DataRequired(), user_exists])
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(),
            Regexp(r'^(?=.*[!@#$%^&+=])', message="Password must contain at least one special character (!, @, #, etc.)"),
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

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        'Password', 
        validators=[
            DataRequired(),
            # Ensure at least one special character
            Regexp(r'^(?=.*[!@#$%^&+=])', message="Password must contain at least one special character (!, @, #, etc.)"),
            # Ensure no forbidden characters are used
            check_forbidden_characters
        ]
    )
    confirm_password = PasswordField('Retype Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords must match")])
    submit = SubmitField('Reset Password')

    submit = Submit = SubmitField('Submit')
    
class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    location_option = RadioField(
        'Location Option',
        choices=[('current', 'Use Current Location'), ('address', 'Enter Address')],
        default='current',
        validators=[DataRequired()]
    )
    address = StringField('Address', validators=[Length(max=255)])  # Optional address
    location = SelectField('Suggested Locations', choices=[], validators=[DataRequired()])
    required_attendees = SelectMultipleField('Required Attendees (Usernames)', choices=[], coerce=int)
    optional_attendees = SelectMultipleField('Optional Attendees (Usernames)', choices=[], coerce=int)
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Submit')


class FeedbackForm(FlaskForm):
    content = TextAreaField(
        'Your Feedback', 
        validators=[
            DataRequired(message="Feedback cannot be empty."),
            Length(max=1000, message="Feedback must be under 1000 characters.")
        ]
    )
    submit = SubmitField('Submit Feedback')
