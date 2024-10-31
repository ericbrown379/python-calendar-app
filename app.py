from flask import Flask, render_template, redirect, url_for, flash, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm, EventForm
from datetime import date, timedelta, datetime
from event_manager import EventManager
from zoneinfo import ZoneInfo
from email_manager import check_email_exists, send_email_via_gmail_oauth2, send_verification_email
import os
from flask_migrate import Migrate 
from models import User, Event, db
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)  # Set up Flask-Migrate here

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

event_manager = EventManager()

# Define timezone for Eastern Time (US/Michigan)
#eastern = ZoneInfo("America/Detroit")

# Print database information
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Absolute path to database:", os.path.abspath('calendar.db'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to format time to AM/PM format
def format_time_am_pm(time_obj):
    """Convert a time object to 12-hour AM/PM format."""
    return time_obj.strftime('%I:%M %p')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('week_view'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_verified:  # Check if the user is verified
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('week_view'))  # Change to your dashboard route
            else:
                flash('Please verify your email before logging in.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()  # Commit to generate the user ID
            print(f"User ID: {user.id}")  # Debugging line
            user.token = user.generate_verification_token()  # Ensure this method returns a valid token
            print(f"Token generated: {user.token}")  # Debugging line
            if user.token:
                send_verification_email(user.email, user.username, user.token)
                flash('Account created! Please check your email to verify your account.', 'success')
                return redirect(url_for('login'))
            else:
                print("Token generation failed")  # Log failure
                flash('Error generating verification token', 'danger')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            print(f"Exception occurred: {e}")  # Log the exception
            flash('An error occurred while creating your account.', 'danger')
    return render_template('register.html', form=form)

@app.route('/verify_email/<token>')
def verify_email(token):
    user_id = verify_token(token)
    if user_id is None:
        flash('Verification link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user:
        user.is_verified = True
        db.session.commit()
        flash('Email verified successfully!', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('login'))

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print("RETURN USER ID",payload['user_id'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None  # Return None if the token is invalid or expired
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/week', methods=['GET'], endpoint='week_view')
@login_required
def week_view():
    # Get the current date
    today = date.today()
    
    # Create a range of dates from today to the next 6 days
    weekly_dates = [today + timedelta(days=i) for i in range(7)]
    
    # Dictionary to store events by date
    weekly_events = {}

    # Fetch events for each day in the 7-day range starting from today
    for single_date in weekly_dates:
        events_for_day = event_manager.get_events_by_date(current_user.id, single_date)
        # Display time in AM/PM format for each event
        for event in events_for_day:
            event.start_time = format_time_am_pm(datetime.strptime(event.start_time, '%H:%M:%S'))
            event.end_time = format_time_am_pm(datetime.strptime(event.end_time, '%H:%M:%S'))
        weekly_events[single_date] = events_for_day

    return render_template('week_view.html', weekly_events=weekly_events)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        # Store times in Eastern Time (no UTC conversion)
        start_time = form.start_time.data.strftime('%H:%M:%S')
        end_time = form.end_time.data.strftime('%H:%M:%S')

        # Add the event for the current user
        event_manager.add_event(
            name=form.name.data,
            date=form.date.data,
            start_time=start_time,
            end_time=end_time,
            description=form.description.data,
            user_id=current_user.id
        )
        flash('Event added!', 'success')
        return redirect(url_for('week_view'))
    return render_template('add_event.html', form=form)

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = event_manager.storage_manager.retrieve_event(event_id)

    if event.user_id != current_user.id:
        flash("You are not authorized to edit this event.", 'danger')
        return redirect(url_for('week_view'))

    # Convert the date string back to a date object and times back to time objects
    event.date = datetime.strptime(event.date, '%Y-%m-%d').date()  # Convert string to date object
    event.start_time = datetime.strptime(event.start_time, '%H:%M:%S').time()  # Convert string to time object
    event.end_time = datetime.strptime(event.end_time, '%H:%M:%S').time()  # Convert string to time object

    form = EventForm(obj=event)

    if form.validate_on_submit():
        # Store times in Eastern Time (no UTC conversion)
        start_time = form.start_time.data.strftime('%H:%M:%S')
        end_time = form.end_time.data.strftime('%H:%M:%S')

        event_manager.edit_event(
            event_id=event_id,
            name=form.name.data,
            date=form.date.data,
            start_time=start_time,
            end_time=end_time,
            description=form.description.data
        )
        flash('Event updated!', 'success')
        return redirect(url_for('week_view'))

    return render_template('edit_event.html', form=form, event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = event_manager.storage_manager.retrieve_event(event_id)
    if event.user_id != current_user.id:
        flash("You are not authorized to delete this event.", 'danger')
        return redirect(url_for('week_view'))

    event_manager.delete_event(event_id)
    flash('Event deleted!', 'success')
    return redirect(url_for('week_view'))



from flask.cli import with_appcontext
import click

@app.cli.command("set-default-emails")
@with_appcontext
def set_default_emails():
    null_email_users = User.query.filter(User.email.is_(None)).all()
    for user in null_email_users:
        user.email = 'default@example.com'  # Set a default email or handle accordingly
    db.session.commit()  # Commit changes to the database
    click.echo(f"Updated {len(null_email_users)} users with a default email.")

@app.cli.command("reset-db")
def reset_db():
    """Reset the database by dropping all tables and recreating them."""
    with app.app_context():
        db.drop_all()  # Drop all tables
        db.create_all()  # Create all tables
        click.echo("Database reset successfully.")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

