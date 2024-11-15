from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import jwt #PYJWT ALL JWT ARE PYJWT NOT JWT
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
    token = db.Column(db.String(200), nullable=True)  # New column for the verification token
    is_verified = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the provided password against the stored password hash."""
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self, expiration=3600):  # 1 hour expiration
        from app import app
        current_utc_time = datetime.now(timezone.utc)
        payload = {
            'user_id': self.id,
            'exp': current_utc_time + timedelta(hours=1)
        } 
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def retrieve_user_by_id(user_id):
    """Retrieve a user by their ID."""
    return User.query.filter_by(id=user_id).first()

def retrieve_user_by_email(email):
    """Retrieve a user by their ID."""
    return User.query.filter_by(email=email).first()

class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    end_time = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)  # Add a location field if needed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('events', lazy=True))


    # Relationships for attendees
    required_attendees = db.relationship('User', secondary=required_attendees, backref='required_events')
    optional_attendees = db.relationship('User', secondary=optional_attendees, backref='optional_events')

    user = db.relationship('User', backref=db.backref('created_events', lazy=True))

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True) 
    content = db.Column(db.Text, nullable=False)  # Store the feedback text


