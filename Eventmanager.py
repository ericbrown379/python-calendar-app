import events

class EventManager:
    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)
        return self.events
    
    def edit_event(self, event_name):
        if event in self.events:
            for event in self.events:
                if event.name == event_name:

                 return event
    
    def delete_event(self, event):

        return
    
    def get_events_by_date(self, date):

        for event in event:
            if event.date == date:
                return event

            return event


    events = []
