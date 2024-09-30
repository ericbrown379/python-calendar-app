from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, TimeField
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
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Submit')