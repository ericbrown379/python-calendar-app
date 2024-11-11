from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
    address = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the provided password against the stored password hash."""
        return check_password_hash(self.password_hash, password)


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

    # Relationships for attendees
    required_attendees = db.relationship('User', secondary=required_attendees, backref='required_events')
    optional_attendees = db.relationship('User', secondary=optional_attendees, backref='optional_events')

    user = db.relationship('User', backref=db.backref('created_events', lazy=True))

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True) 
    content = db.Column(db.Text, nullable=False)  # Store the feedback text


