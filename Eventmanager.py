from Event import Event
from StorageManager import StorageManager


class EventManager:
    """Manages business logic for event-related operations"""

    def __init__(self):
        """Initialize the EventManager and connect to StorageManager."""
        self.storage_manager = StorageManager()

    def add_event(self, name, date, start_time, end_time, description, user_id):
        """
        Add a new event.
        :param name: Name of the event.
        :param date: Date of the event.
        :param start_time: Start time of the event.
        :param end_time: End time of the event.
        :param description: Description of the event.
        :param user_id: ID of the user creating the event.
        :return: None
        """
        # Generate event_id (could be auto-incremented by DB, but for now, we're using a custom ID generation)
        event_id = self.storage_manager.get_next_event_id()

        # Create a new Event object
        event = Event(event_id, name, date, start_time, end_time, description)

        # Store the event in the database using the StorageManager
        self.storage_manager.insert_event(event, user_id)

    def edit_event(self, event_id, name=None, date=None, start_time=None, end_time=None, description=None):
        """
        Edit an existing event.
        :param event_id: ID of the event to edit.
        :param name: (Optional) New name for the event.
        :param date: (Optional) New date for the event.
        :param start_time: (Optional) New start time for the event.
        :param end_time: (Optional) New end time for the event.
        :param description: (Optional) New description for the event.
        :return: Updated event object, or None if not found.
        """
        # Retrieve the event by its ID
        event = self.storage_manager.retrieve_event(event_id)

        if event:
            # Update event details
            event.update_event(name=name, date=date, start_time=start_time, end_time=end_time, description=description)
            # Save the updated event back to the database
            self.storage_manager.update_event(event)
            return event

        return None  # Return None if event not found

    def delete_event(self, event_id):
        """
        Delete an event.
        :param event_id: ID of the event to delete.
        :return: None
        """
        self.storage_manager.delete_event(event_id)

    def get_events_by_date(self, user_id, date):
        """
        Get all events for a specific date for a user.
        :param user_id: ID of the user.
        :param date: The date to retrieve events for.
        :return: List of Event objects.
        """
        return self.storage_manager.retrieve_events_by_date(user_id, date)

    def search_events(self, user_id, keyword=None, date=None):
        """
        Search for events by keyword or date.
        :param user_id: ID of the user performing the search.
        :param keyword: (Optional) Keyword to search in event names or descriptions.
        :param date: (Optional) Date to search for events.
        :return: List of Event objects matching the search criteria.
        """
        if date:
            return self.get_events_by_date(user_id, date)
        elif keyword:
            all_events = self.storage_manager.retrieve_events(user_id)  # Retrieve all events for the user
            results = [event for event in all_events if keyword.lower() in event.name.lower() or keyword.lower() in event.description.lower()]
            return results

        return []

    def __del__(self):
        """Destructor to clean up and close connections."""
        del self.storage_manager