# Sample usage of EventManager
from Eventmanager import EventManager
from Event import Event

# Create the event manager
manager = EventManager()

# Add events
event1 = Event(1, "Meeting", "2024-09-28", "09:00", "10:00", "Team meeting")
event2 = Event(2, "Conference", "2024-09-29", "11:00", "13:00", "Tech conference")

manager.add_event(event1)
manager.add_event(event2)

# Edit an event
manager.edit_event(1, name="Team Meeting Update", description="Updated description")

# Get events by date
events_on_28th = manager.get_events_by_date("2024-09-28")
print([e.get_event_details() for e in events_on_28th])

# Search events by keyword
searched_events = manager.search_events(keyword="conference")
print([e.get_event_details() for e in searched_events])

# Delete an event
manager.delete_event(1)