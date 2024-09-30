from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm, EventForm
from models import User, Event, db
from datetime import date, timedelta, datetime
from event_manager import EventManager
from zoneinfo import ZoneInfo
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

event_manager = EventManager()

# Define timezone for Eastern Time (US/Michigan)
eastern = ZoneInfo("America/Detroit")

# Print database information
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Absolute path to database:", os.path.abspath('calendar.db'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to convert input times from Eastern Time to UTC for storage
def convert_time_to_utc(time_obj):
    """Convert a naive datetime time object (input in Eastern Time) to UTC."""
    eastern_time = time_obj.replace(tzinfo=eastern)
    utc_time = eastern_time.astimezone(ZoneInfo('UTC'))
    return utc_time.strftime('%H:%M:%S')

# Helper function to convert UTC time back to Eastern Time for display
def convert_time_to_eastern(utc_time_str):
    """Convert a time string (in 'HH:MM:SS' format) from UTC to Eastern Time and return formatted 'HH:MM AM/PM'."""
    utc_time = datetime.strptime(utc_time_str, '%H:%M:%S')
    utc_time = utc_time.replace(tzinfo=ZoneInfo('UTC'))
    eastern_time = utc_time.astimezone(eastern)
    return eastern_time.strftime('%I:%M %p')

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
            login_user(user)
            return redirect(url_for('week_view'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Account created!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('There was an issue creating your account.', 'danger')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
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
        # Convert stored UTC times to Eastern Time for display
        for event in events_for_day:
            event.start_time = convert_time_to_eastern(event.start_time)
            event.end_time = convert_time_to_eastern(event.end_time)
        weekly_events[single_date] = events_for_day

    return render_template('week_view.html', weekly_events=weekly_events)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        # Convert times from Eastern Time to UTC before storing
        start_time_utc = convert_time_to_utc(form.start_time.data)
        end_time_utc = convert_time_to_utc(form.end_time.data)

        # Add the event for the current user
        event_manager.add_event(
            name=form.name.data,
            date=form.date.data,
            start_time=start_time_utc,
            end_time=end_time_utc,
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

    # Convert stored UTC times back to Eastern Time for the form
    event.start_time = datetime.strptime(event.start_time, '%H:%M:%S').time()
    event.end_time = datetime.strptime(event.end_time, '%H:%M:%S').time()

    form = EventForm(obj=event)

    if form.validate_on_submit():
        # Convert times from Eastern Time to UTC before saving
        start_time_utc = convert_time_to_utc(form.start_time.data)
        end_time_utc = convert_time_to_utc(form.end_time.data)

        event_manager.edit_event(
            event_id=event_id,
            name=form.name.data,
            date=form.date.data,
            start_time=start_time_utc,
            end_time=end_time_utc,
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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)