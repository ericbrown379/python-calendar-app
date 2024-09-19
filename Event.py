class Event:
    START_TIME = ""
    END_TIME = ""
    DESCRIPTION = ""

    def __init__(self, start, end, desc):
        """Constrctor for the Event class, added simple definitions - MC 9/19/24"""
        self.START_TIME = start
        self.END_TIME = end
        self.DESCRIPTION = desc