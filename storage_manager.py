from datetime import date, datetime
from models import Event, db  # Import SQLAlchemy Event model and db

class StorageManager:
    """Handles SQLAlchemy database interactions for event storage and retrieval."""


    def insert_event(self, event: Event):
        """Insert an event into the database using SQLAlchemy."""
        try:
            print(f"\nInserting event in storage manager:")
            print(f"Name: {event.name}")
            print(f"Date: {event.date}")
            print(f"Start Time: {event.start_time}")
            print(f"End Time: {event.end_time}")
            
            db.session.add(event)
            db.session.commit()
            
            print(f"Event inserted successfully with ID: {event.id}")
            return True
        except Exception as e:
            print(f"Error inserting event in storage manager: {str(e)}")
            db.session.rollback()
            return False

    def retrieve_event(self, event_id: int) -> Event:
        """Retrieve a single event by event_id using SQLAlchemy."""
        return Event.query.get(event_id)
    
    def retrieve_events_by_date(self, user_id: int, target_date) -> list:
        """Retrieve all events for a user on a specific date using SQLAlchemy."""
        try:
            # Convert the target_date to string format
            if isinstance(target_date, (datetime, date)):
                date_str = target_date.strftime('%Y-%m-%d')
            else:
                date_str = str(target_date)
            
            print(f"Searching for events on date: {date_str} for user: {user_id}")
            events = Event.query.filter_by(user_id=user_id, date=date_str).all()
            print(f"Found {len(events)} events")
            for event in events:
                print(f"Event: {event.name} at {event.start_time}")
            return events
        except Exception as e:
            print(f"Error retrieving events: {str(e)}")
            return []
        
    def retrieve_events(self, user_id: int) -> list:
        """Retrieve all events for a user using SQLAlchemy."""
        try:
            events = Event.query.filter_by(user_id=user_id).all()
            print(f"Retrieved {len(events)} events for user {user_id}")
            for event in events:
                print(f"Event: {event.name} on {event.date}")
            return events
        except Exception as e:
            print(f"Error retrieving events: {str(e)}")
            return []

    def update_event(self, event: Event):
        """Update an event's details in the database using SQLAlchemy."""
        try:
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error updating event: {str(e)}")
            db.session.rollback()
            return False
        
    def delete_event(self, event_id: int):
        """Delete an event from the database using SQLAlchemy."""
        try:
            event = self.retrieve_event(event_id)
            if event:
                db.session.delete(event)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting event: {str(e)}")
            db.session.rollback()
            return False