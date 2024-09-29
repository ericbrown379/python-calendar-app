from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm, EventForm
from models import User, Event, db
from datetime import date, timedelta
from event_manager import EventManager
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

# Print database information
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Absolute path to database:", os.path.abspath('calendar.db'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Root route, redirect to login or week view depending on if the user is logged in
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
            print("Error:", e)
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
    # Calculate the start and end of the week
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Dictionary to store events by date
    weekly_events = {}
    
    # Fetch events for each day in the week range
    for single_date in (start_of_week + timedelta(n) for n in range(7)):
        events_for_day = event_manager.get_events_by_date(current_user.id, single_date)
        weekly_events[single_date] = events_for_day

    # Pass the weekly_events to the template
    return render_template('week_view.html', weekly_events=weekly_events)


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        # Convert time objects to strings before storing them
        start_time_str = form.start_time.data.strftime('%H:%M:%S')
        end_time_str = form.end_time.data.strftime('%H:%M:%S')

        # Add the event for the current user
        event_manager.add_event(
            name=form.name.data,
            date=form.date.data,
            start_time=start_time_str,
            end_time=end_time_str,
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

    form = EventForm(obj=event)
    if form.validate_on_submit():
        event_manager.edit_event(
            event_id=event_id,
            name=form.name.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            description=form.description.data
        )
        flash('Event updated!', 'success')
        return redirect(url_for('week_view'))
    return render_template('edit_event.html', form=form, event=event)

print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Absolute path to database:", os.path.abspath('calendar.db'))

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