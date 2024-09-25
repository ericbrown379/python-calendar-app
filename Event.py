class Event:
    START_TIME = ""
    END_TIME = ""
    DATE = ""
    DESCRIPTION = ""

    def __init__(self, start, end, date, desc):
        """Constrctor for the Event class, added simple definitions - MC 9/19/24"""
        self.START_TIME = start
        self.END_TIME = end
        self.DESCRIPTION = desc
        self.DATE = date