from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone

db = SQLAlchemy()

required_attendees = db.Table(
    'required_attendees',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

optional_attendees = db.Table(
    'optional_attendees',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(200), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)

    notifications_enabled = db.Column(db.Boolean, default=False, nullable=False)
    notification_hours = db.Column(db.Integer, default=1, nullable=False)  # Default to 1 hour if not set


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self, expiration=3600):
        from backend.app import app
        current_utc_time = datetime.now(timezone.utc)
        payload = {
            'user_id': self.id,
            'exp': current_utc_time + timedelta(hours=1)
        } 
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(50), nullable=False)  # Stored as 'YYYY-MM-DD'
    start_time = db.Column(db.String(50), nullable=False)  # Stored as 'HH:MM:SS'
    end_time = db.Column(db.String(50), nullable=False)  # Stored as 'HH:MM:SS'
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_hours = db.Column(db.Integer, nullable=True)

    required_attendees = db.relationship('User', secondary=required_attendees, backref='required_events')
    optional_attendees = db.relationship('User', secondary=optional_attendees, backref='optional_events')
    user = db.relationship('User', backref=db.backref('created_events', lazy=True))

    # Add helper methods for date/time handling
    def get_date_formatted(self):
        """Return date as a datetime.date object"""
        return datetime.strptime(self.date, '%Y-%m-%d').date()

    def get_start_time_formatted(self):
        """Return start time in AM/PM format"""
        time_obj = datetime.strptime(self.start_time, '%H:%M:%S')
        return time_obj.strftime('%I:%M %p')

    def get_end_time_formatted(self):
        """Return end time in AM/PM format"""
        time_obj = datetime.strptime(self.end_time, '%H:%M:%S')
        return time_obj.strftime('%I:%M %p')

    def __repr__(self):
        return f'<Event {self.name} on {self.date} at {self.start_time}>'
    

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True) 
    content = db.Column(db.Text, nullable=False)

class UserPreferences(db.Model):
    __tablename__ = "user_preferences"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    preferred_days = db.Column(db.String(50))
    preferred_times = db.Column(db.String(50))
    location_preferences = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class EventSuggestion(db.Model):
    __tablename__ = "event_suggestion"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_name = db.Column(db.String(150), nullable=False)
    suggested_date = db.Column(db.Date, nullable=False)
    suggested_time = db.Column(db.String(50), nullable=False)
    explanation = db.Column(db.Text)
    similarity_score = db.Column(db.Float)
    is_dismissed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def retrieve_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()

def retrieve_user_by_email(email):
    return User.query.filter_by(email=email).first()


# block out time

class BlockedTime(db.Model):
    __tablename__ = 'blocked_time'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    recurring = db.Column(db.String(10), nullable=True)  # Options: 'daily', 'weekly', 'none'
    description = db.Column(db.String(200), nullable=True)

    # Establish relationship with User
    user = db.relationship('User', backref=db.backref('blocked_times', lazy=True))

    def __repr__(self):
        return f'<BlockedTime {self.start_time} to {self.end_time} for user {self.user_id}>'
