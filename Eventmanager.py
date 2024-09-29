from Event import Event

class EventManager:
    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)
    
    def edit_event(self, event_id, name=None, date=None, start_time=None, end_time=None, description=None):
        for event in self.events:
            if event.event_id == event_id:
                event.update_event(name, date, start_time, end_time, description)
                return event
    
    def delete_event(self, event):

        return
    
    def get_events_by_date(self, date):

        for event in event:
            if event.date == date:
                return event

            return event


    events = []
