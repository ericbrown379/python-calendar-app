
from storage_manager import StorageManager
from models import Event

class EventManager:
    """Manages business logic for event-related operations"""

    def __init__(self):
        """Initialize the EventManager with SQLAlchemy session."""
        self.storage_manager = StorageManager()

    def add_event(self, name, date, start_time, end_time, description, user_id):
        """Add a new event using SQLAlchemy."""
        event = Event(
            name=name,
            date=date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            user_id=user_id
        )
        self.storage_manager.insert_event(event)

    def edit_event(self, event_id, name=None, date=None, start_time=None, end_time=None, description=None):
        """Edit an existing event using SQLAlchemy."""
        event = self.storage_manager.retrieve_event(event_id)
        if event:
            event.name = name or event.name
            event.date = date or event.date
            event.start_time = start_time or event.start_time
            event.end_time = end_time or event.end_time
            event.description = description or event.description
            self.storage_manager.update_event(event)
            return event
        return None

    def delete_event(self, event_id):
        """Delete an event using SQLAlchemy."""
        self.storage_manager.delete_event(event_id)

    def get_events_by_date(self, user_id, date):
        """Get all events for a specific date for a user."""
        return self.storage_manager.retrieve_events_by_date(user_id, date)

    def search_events(self, user_id, keyword=None, date=None):
        """Search for events by keyword or date."""
        if date:
            return self.get_events_by_date(user_id, date)
        elif keyword:
            all_events = self.storage_manager.retrieve_events(user_id)
            return [event for event in all_events if keyword.lower() in event.name.lower() or keyword.lower() in event.description.lower()]
        return []