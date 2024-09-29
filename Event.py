class Event:

    def __init__(self, event_id, name, date, start_time, end_time, description=""):
        """Constructor for the Event class."""
        self.event_id = event_id
        self.name = name  
        self.date = date  
        self.start_time = start_time  
        self.end_time = end_time  
        self.description = description 
        
    def update_event(self, name=None, date=None, start_time=None, end_time=None, description=None):
        if name:
            self.name = name
        if date:
            self.date = date
        if start_time:
            self.start_time = start_time
        if end_time:
            self.end_time = end_time
        if description:
            self.description = description

    def get_event_details(self):
        return {
            'event_id': self.event_id,
            'name': self.name,
            'date': self.date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'description': self.description
        }
