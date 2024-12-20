from flask import Flask, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import requests
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField, TimeField, SelectMultipleField
from forms import LoginForm, RegisterForm, EventForm, ForgotPasswordForm, ResetPasswordForm, FeedbackForm, AdminLoginForm
from models import User, Event, Feedback,retrieve_user_by_id, retrieve_user_by_email, db
from datetime import date, timedelta, datetime
from event_manager import EventManager
from zoneinfo import ZoneInfo
from email_manager import check_email_exists, send_email_via_gmail_oauth2, send_verification_email, send_password_reset_email
from dotenv import load_dotenv
import os
import jwt
from suggestion_service import EventsuggestionService
suggestion_service = EventsuggestionService()
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, redirect, url_for, flash, request
from models import BlockedTime
from forms import BlockOutTimeForm
from datetime import datetime
from flask_login import login_required, current_user
from sqlalchemy import and_ 
from functools import wraps
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_PLACES_API_KEY'] = os.getenv('GOOGLE_PLACES_API_KEY')

#Google Analytics API data posting and fetching code

MEASUREMENT_ID = os.getenv('GA_MEASUREMENT_ID')
API_SECRET = os.getenv('GA_API_SECRET')

def send_event_to_google_analytics(event_name):
    if not MEASUREMENT_ID or not API_SECRET:
        raise ValueError("Missing GA_MEASUREMENT_ID or GA_API_SECRET in the environment.")
    
    client_id = "1234567890.1234567890"  # Replace with dynamically generated client_id if needed
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": event_name,
                "params": {
                    "value": 1
                }
            }
        ]
    }

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}"

    try:
        response = requests.post(
            f"https://www.google-analytics.com/mp/collect?measurement_id={MEASUREMENT_ID}&api_secret={API_SECRET}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:
            print(f"Event '{event_name}' sent successfully to Google Analytics.")
        else:
            print(f"Error sending event '{event_name}': {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")


db.init_app(app)
migrate = Migrate(app, db)  # Set up Flask-Migrate here

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

scheduler = BackgroundScheduler()
scheduler.start()

event_manager = EventManager()

# Define timezone for Eastern Time (US/Michigan)
#eastern = ZoneInfo("America/Detroit")

# Print database information
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("Absolute path to database:", os.path.abspath('calendar.db'))

# Make API KEY availiable to all templates
@app.context_processor
def inject_google_api_key():
    return dict(google_places_api_key=app.config['GOOGLE_PLACES_API_KEY'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# helper function of blocked time
def check_for_blocked_time_conflicts(start_time, end_time):
    """Check if the new event conflicts with blocked times."""
    print(f"Checking for conflicts: {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}")  # Debugging print
    conflict = BlockedTime.query.filter(
        and_(
            BlockedTime.user_id == current_user.id,
            BlockedTime.start_time < end_time,  # Blocked time starts before the event ends
            BlockedTime.end_time > start_time   # Blocked time ends after the event starts
        )
    ).first()
    if conflict:
        print(f"Conflict detected: Blocked from {conflict.start_time.strftime('%I:%M %p')} to {conflict.end_time.strftime('%I:%M %p')}")  # Debugging print
    else:
        print("No conflicts detected.")  # Debugging print
    return conflict




# Helper function to format time to AM/PM format
def format_time_am_pm(time_obj):
    """Convert a time object to 12-hour AM/PM format."""
    return time_obj.strftime('%I:%M %p')


@app.route('/api/suggestions/event', methods=['GET'])
@login_required
def get_event_suggestions():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter is required '}, 400)
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        suggestions = suggestion_service.get_suggestions(current_user.id, target_date)
        return jsonify({
            'suggestions': [{
                'id': s.id,
                'name': s.event_name,
                'time': s.suggested_time,
                'explanation': s.explanation,
                'score': s.similarity_score
            } for s in suggestions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/suggestions/dismiss/<int:suggestion_id>', methods=['POST'])
@login_required
def dismiss_suggestion(suggestion_id):
    feedback = request.json.get('feedback')
    suggestion_service.dismiss_suggestion(suggestion_id, feedback)
    return jsonify({'status': 'success'})


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

@app.route('/api/suggestions')
def get_suggestions():
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    if lat and lng:
        suggestions = event_manager.suggest_locations((float(lat), float(lng)))
        return jsonify({'suggestions': suggestions})
    return jsonify({'suggestions': []})


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
                flash('There was an error generating your verification token.', 'danger')
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
        flash('User was not found, please try verifying again!.', 'danger')
    return redirect(url_for('login'))

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        form = ResetPasswordForm()
        user_id = verify_token(token)  # Use consistent lowercase for user_id
        # Check if token is valid and user exists
        if user_id is None:
            print("No user_id found")
            flash("Invalid or expired token, please request a new password reset.", "danger")
            return redirect(url_for('login'))
        user = retrieve_user_by_id(user_id=user_id)
        if user is None:
            print("No user object")
            flash("User not found, please request a new password reset.", "danger")
            return redirect(url_for('login'))
        if form.validate_on_submit():
            print(f"Updating password for user {user.id}")
            user.set_password(form.new_password.data)  # Ensure this saves the user object
            db.session.commit()  # Commit the transaction to save changes
            flash('Your password has been updated successfully. Redirecting to login page.', "success")
            return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Exception occurred: {e}")  # Log the exception
        flash('An error occurred while resetting your password.', 'danger')
    return render_template('reset_password.html', form=form, token=token)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')



def verify_event_storage():
    """Verify events are stored and retrieved correctly"""
    try:
        print("\nVerifying event storage:")
        
        # Get all events
        all_events = Event.query.all()
        print(f"Total events in database: {len(all_events)}")
        
        for event in all_events:
            print(f"\nEvent ID: {event.id}")
            print(f"Name: {event.name}")
            print(f"Date: {event.date}")
            print(f"Time: {event.start_time} - {event.end_time}")
            print(f"User ID: {event.user_id}")
            
            # Verify we can retrieve it
            retrieved = event_manager.storage_manager.retrieve_event(event.id)
            if retrieved:
                print("Successfully retrieved event")
            else:
                print("Failed to retrieve event")
                
    except Exception as e:
        print(f"Error verifying events: {str(e)}")

@app.route('/faq', methods=['GET', 'POST'])
def faq():
    form = FeedbackForm()  # Instantiate your form
    if form.validate_on_submit():
        try:
            # Assuming `user_id` and `event_id` are optional or dynamically determined elsewhere in the application
            feedback = Feedback(content=form.content.data)
            db.session.add(feedback)
            db.session.commit()
            flash('We received your feedback, Thank You!', 'success')
            return redirect(url_for('week_view'))  # Redirect to avoid form resubmission on refresh
        except Exception as e:
            print(e)
            flash('There was an error submitting your feedback.', 'danger')
    return render_template('faq.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    try:
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            email = form.email.data
            user = retrieve_user_by_email(email)
            token = user.generate_verification_token()
            send_password_reset_email(user.email, user.username, token=token)
            flash("Please check your email for a reset link.", "success")
            #Redirect to create new password url
        return render_template('forgot_password.html', form=form)
    except Exception as e:
        print(e)
        flash("There was an error submitting your request, please try again!", "danger")

from flask_login import current_user

@app.route('/week', methods=['GET', 'POST'], endpoint='week_view')
@login_required
def week_view():
    try:
        # Get the current date
        today = date.today()
        print(f"\nDisplaying week view starting from: {today}")
        
        # Create a range of dates from today to the next 6 days
        weekly_dates = [today + timedelta(days=i) for i in range(7)]
        
        # Dictionary to store events by date
        weekly_events = {}
        
        # Debug: Show all events for current user
        all_events = Event.query.filter_by(user_id=current_user.id).all()
        print(f"\nAll events for user {current_user.id}:")
        for event in all_events:
            print(f"Event: {event.name} on {event.date}")
        
        # Fetch events for each day
        for single_date in weekly_dates:
            date_str = single_date.strftime('%Y-%m-%d')
            print(f"\nFetching events for {date_str}")
            
            # Get events for this date
            events = Event.query.filter_by(
                user_id=current_user.id,
                date=date_str
            ).all()
            
            print(f"Found {len(events)} events")
            
            # Format times for display
            for event in events:
                print(f"Processing event: {event.name}")
                try:
                    start_time = datetime.strptime(event.start_time, '%H:%M:%S')
                    end_time = datetime.strptime(event.end_time, '%H:%M:%S')
                    event.start_time = start_time.strftime('%I:%M %p')
                    event.end_time = end_time.strftime('%I:%M %p')
                    print(f"Formatted times: {event.start_time} - {event.end_time}")
                except Exception as e:
                    print(f"Error formatting time for event {event.id}: {str(e)}")
            
            weekly_events[single_date] = events
        
        print("\nReturning weekly events:", weekly_events)
        return render_template('week_view.html', weekly_events=weekly_events, user=current_user)
    except Exception as e:
        print(f"Error in week_view: {str(e)}")
        flash('Error loading calendar. Please try again.', 'danger')
        return render_template('week_view.html', weekly_events={}, user=current_user)
    

@app.route('/debug/events')
@login_required
def debug_events():
    """Debug endpoint to view all events in the database"""
    try:
        events = Event.query.filter_by(user_id=current_user.id).all()
        events_data = [
            {
                'id': event.id,
                'name': event.name,
                'date': event.date,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'location': event.location
            }
            for event in events
        ]
        return jsonify({'events': events_data})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/debug/verify_event/<int:event_id>')
@login_required
def verify_event(event_id):
    """Debug endpoint to verify a specific event"""
    try:
        event = Event.query.get(event_id)
        if event:
            return jsonify({
                'id': event.id,
                'name': event.name,
                'date': event.date,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'location': event.location,
                'user_id': event.user_id
            })
        return jsonify({'error': 'Event not found'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    try:
        form = EventForm()

        # Populate attendees
        all_users = User.query.all()
        form.required_attendees.choices = [(user.id, user.username) for user in all_users]
        form.optional_attendees.choices = [(user.id, user.username) for user in all_users]

        if request.method == 'POST':
            print("Form data received:", request.form)  # Debugging print
            
            # Get location from the form data
            location = request.form.get('location')
            print(f"Location from form: {location}")  # Debugging print

            # Set location in the form
            form.location.choices = [(location, location)] if location else [('', 'No location')]
            form.location.data = location

            # Set default notification hours if none provided
            if not form.notification_hours.data:
                form.notification_hours.data = '1'

            if form.validate_on_submit():
                # Format the date and times
                start_time = datetime.combine(form.date.data, form.start_time.data)
                end_time = datetime.combine(form.date.data, form.end_time.data)

                print(f"Adding event from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}")  # Debugging print

                # Check for blocked time conflicts
                conflict = check_for_blocked_time_conflicts(start_time, end_time)
                if conflict:
                    flash(
                        f"Event conflicts with blocked time: {conflict.start_time.strftime('%I:%M %p')} "
                        f"to {conflict.end_time.strftime('%I:%M %p')}", 
                        "danger"
                    )
                    print(f"Conflict detected with blocked time: {conflict.start_time} to {conflict.end_time}")  # Debugging print
                    return redirect(url_for('add_event'))

                # Proceed with event creation if no conflict
                event = event_manager.add_event(
                    name=form.name.data,
                    date=form.date.data.strftime('%Y-%m-%d'),
                    start_time=start_time.strftime('%H:%M:%S'),
                    end_time=end_time.strftime('%H:%M:%S'),
                    location=location,
                    description=form.description.data,
                    user_id=current_user.id,
                    required_attendees=form.required_attendees.data,
                    optional_attendees=form.optional_attendees.data
                )

                if event:
                    db.session.commit()  # Commit the new event
                    send_event_to_google_analytics('event_created')
                    flash('Event added successfully!', 'success')
                    return redirect(url_for('week_view'))
                else:
                    flash('Error creating event. Please try again.', 'danger')
            else:
                # Log form validation errors
                print("Form validation errors:", form.errors)
                flash('Form validation failed. Please check your input.', 'danger')

    except Exception as e:
        # Log the exception and rollback if needed
        print(f"Error in add_event route: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'danger')

    return render_template('add_event.html', form=form)


@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    try:
        # Retrieve the event to be edited
        event = event_manager.storage_manager.retrieve_event(event_id)
        if not event:
            flash('Event not found.', 'danger')
            return redirect(url_for('week_view'))

        # Ensure the current user is authorized to edit the event
        if event.user_id != current_user.id:
            flash("You are not authorized to edit this event.", 'danger')
            return redirect(url_for('week_view'))

        # Initialize the event form
        form = EventForm()

        if request.method == 'GET':
            # Populate the form with existing event data
            form.name.data = event.name
            form.date.data = datetime.strptime(event.date, '%Y-%m-%d').date()
            form.start_time.data = datetime.strptime(event.start_time, '%H:%M:%S').time()
            form.end_time.data = datetime.strptime(event.end_time, '%H:%M:%S').time()
            form.description.data = event.description
            form.location.data = event.location
            if hasattr(event, 'notification_hours') and event.notification_hours:
                form.notification_hours.data = str(event.notification_hours)

        if request.method == 'POST':
            print("Form data received:", request.form)  # Debugging print

            # Get location from the form data
            location = request.form.get('location')
            form.location.choices = [(location, location)] if location else [('', 'No location')]
            form.location.data = location

            if form.validate_on_submit():
                print("Form validated successfully")  # Debugging print

                # Convert form data to strings
                date_str = form.date.data.strftime('%Y-%m-%d')
                start_time = datetime.combine(form.date.data, form.start_time.data)
                end_time = datetime.combine(form.date.data, form.end_time.data)

                print(f"Checking conflicts for {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}")  # Debugging print

                # Check for conflicts with blocked times (excluding the event being edited)
                conflict = BlockedTime.query.filter(
                    and_(
                        BlockedTime.user_id == current_user.id,
                        BlockedTime.start_time < end_time,  # Blocked time starts before the event ends
                        BlockedTime.end_time > start_time   # Blocked time ends after the event starts
                    )
                ).first()

                if conflict:
                    flash(
                        f"Event conflicts with blocked time: {conflict.start_time.strftime('%I:%M %p')} "
                        f"to {conflict.end_time.strftime('%I:%M %p')}", 
                        "danger"
                    )
                    print(f"Conflict detected with blocked time: {conflict.start_time} to {conflict.end_time}")  # Debugging print
                    return redirect(url_for('edit_event', event_id=event.id))

                # Update the event if no conflicts
                updated_event = event_manager.edit_event(
                    event_id=event_id,
                    name=form.name.data,
                    date=date_str,
                    start_time=start_time.strftime('%H:%M:%S'),
                    end_time=end_time.strftime('%H:%M:%S'),
                    location=location,
                    description=form.description.data
                )

                if updated_event:
                    db.session.commit()
                    send_event_to_google_analytics('event_edited')
                    flash('Event updated successfully!', 'success')
                    return redirect(url_for('week_view'))
                else:
                    flash('Failed to update event.', 'danger')

            else:
                print("Form validation failed:", form.errors)  # Debugging print
                flash('Please check your input.', 'danger')

        return render_template('edit_event.html', form=form, event=event, google_api_key=app.config['GOOGLE_PLACES_API_KEY'])

    except Exception as e:
        print(f"Error in edit_event route: {str(e)}")  # Debugging print
        flash('An error occurred while updating the event.', 'danger')
        return redirect(url_for('week_view'))



@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = event_manager.storage_manager.retrieve_event(event_id)
    if event.user_id != current_user.id:
        flash("You are not authorized to delete this event.", 'danger')
        return redirect(url_for('week_view'))

    event_manager.delete_event(event_id)
    send_event_to_google_analytics('event_deleted')
    flash('Event deleted!', 'success')
    return redirect(url_for('week_view'))

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print("RETURN USER ID",payload['user_id'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None  # Return None if the token is invalid or expired
        
def check_for_notifications():
    # Get current time
    now = datetime.now()
    # Query users who have enabled notifications
    users = User.query.filter_by(notifications_enabled=True).all()
    for user in users:
        events = Event.query.filter(Event.date >= now).all()  # Get events that are coming up
        for event in events:
            # Calculate time difference from now to event's start time
            time_to_event = event.date - now
            #if time_to_event <= timedelta(hours=user.notification_hours):
            if True:
                subject = f"Reminder: {event.name} in {event.start_time.strftime('%H:%M')}"
                body = f"Hi,\n\nThis is a reminder that the event '{event.name}' will start at {event.start_time.strftime('%H:%M')}.\n\nBest regards,\nYour Calendar App"
                send_email_via_gmail_oauth2(user.email, subject, body)
@app.before_request
def start_scheduler():
    print("Scheduler running!")
    if not scheduler.running:
        scheduler.start()


@app.route('/block_time', methods=['GET', 'POST'])
@login_required
def block_time():
    form = BlockOutTimeForm()
    if form.validate_on_submit():
        # Create a new blocked time
        blocked_time = BlockedTime(
            user_id=current_user.id,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            recurring=form.recurring.data if form.recurring.data != 'none' else None,
            description=form.description.data
        )
        db.session.add(blocked_time)
        db.session.commit()
        flash("Time blocked successfully!", "success")
        return redirect(url_for('week_view'))
    return render_template('block_time.html', form=form)



# Route to edit a blocked time
@app.route('/edit_block/<int:block_id>', methods=['GET', 'POST'])
@login_required
def edit_block(block_id):
    blocked_time = BlockedTime.query.get_or_404(block_id)
    
    # Ensure only the owner can edit
    if blocked_time.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('week_view'))
    
    form = BlockOutTimeForm(obj=blocked_time)
    if form.validate_on_submit():
        # Update the blocked time details
        blocked_time.start_time = form.start_time.data
        blocked_time.end_time = form.end_time.data
        blocked_time.recurring = form.recurring.data if form.recurring.data != 'none' else None
        blocked_time.description = form.description.data
        db.session.commit()
        flash("Blocked time updated!", "success")
        return redirect(url_for('week_view'))
    
    return render_template('edit_block.html', form=form)


# Route to delete a blocked time
@app.route('/delete_block/<int:block_id>', methods=['POST'])
@login_required
def delete_block(block_id):
    blocked_time = BlockedTime.query.get_or_404(block_id)
    
    # Ensure only the owner can delete
    if blocked_time.user_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for('week_view'))
    
    db.session.delete(blocked_time)
    db.session.commit()
    flash("Blocked time deleted!", "success")
    return redirect(url_for('week_view'))

load_dotenv()
admin_authenticated = False

# Custom decorator to ensure admin authentication
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global admin_authenticated
        if not admin_authenticated:
            flash('Admin login required!', 'danger')
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Login Page that redirects to admin dashboard upon form submission
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global admin_authenticated
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == os.getenv("ADMIN_USERNAME") and form.password.data == os.getenv("ADMIN_PASSWORD"):
            admin_authenticated = True  # Set admin authentication flag
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html', form=form)

# Admin Logout
@app.route('/admin/logout', methods = ['GET', 'POST'])
@admin_login_required
def admin_logout():
    global admin_authenticated
    admin_authenticated = False  # Clear admin authentication flag
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin'))

# Admin Dashboard
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@admin_login_required
def admin_dashboard():
    events = Event.query.join(User).all()
    return render_template('admin_dashboard.html', events=events)

# Function to check if the new event conflicts with a blocked time
def check_for_blocked_time_conflicts(start_time, end_time):
    print(f"Checking for conflicts: {start_time} to {end_time}")  # Debugging print
    conflict = BlockedTime.query.filter(
        and_(
            BlockedTime.user_id == current_user.id,
            BlockedTime.start_time <= end_time,
            BlockedTime.end_time >= start_time
        )
    ).first()
    if conflict:
        print(f"Conflict detected: Blocked from {conflict.start_time} to {conflict.end_time}")  # Debugging print
    else:
        print("No conflicts detected.")  # Debugging print
    return conflict




#FOR DEALING WITH DB ERRORS DURING DEVELOPMENT! CHEAP WORKAROUNDS AND SHOULDN'T BE USED WHEN APP IS DEPLOYED!
#---------------------------------------------------------------------------------------------#
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
#---------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True, port=5000)

