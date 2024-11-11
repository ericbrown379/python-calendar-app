from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, TimeField, SelectField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp

# Custom validator to check for forbidden characters
def check_forbidden_characters(form, field):
    forbidden_characters = set("#$%^&*(){}[]<>?")
    if any(char in forbidden_characters for char in field.data):
        raise ValidationError("Password contains forbidden characters.")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
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
