from models import Event, db  # Import SQLAlchemy Event model and db

class StorageManager:
    """Handles SQLAlchemy database interactions for event storage and retrieval."""

    def insert_event(self, event: Event):
        """Insert an event into the database using SQLAlchemy."""
        db.session.add(event)
        db.session.commit()

    def retrieve_event(self, event_id: int) -> Event:
        """Retrieve a single event by event_id using SQLAlchemy."""
        return Event.query.get(event_id)

    def retrieve_events_by_date(self, user_id: int, date: str):
        """Retrieve all events for a user on a specific date using SQLAlchemy."""
        return Event.query.filter_by(user_id=user_id, date=date).all()

    def retrieve_events(self, user_id: int):
        """Retrieve all events for a user using SQLAlchemy."""
        return Event.query.filter_by(user_id=user_id).all()

    def update_event(self, event: Event):
        """Update an event's details in the database using SQLAlchemy."""
        db.session.commit()

    def delete_event(self, event_id: int):
        """Delete an event from the database using SQLAlchemy."""
        event = self.retrieve_event(event_id)
        if event:
            db.session.delete(event)
            db.session.commit()