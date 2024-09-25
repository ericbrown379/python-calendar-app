class Date:
    # 2D array storing available time intervals (e.g., [[1, 2], [4, 9]])
    dateName = ""
    dayOfWeek = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]  # Set of valid days
    userDataDict = {}

    def __init__(self, dayName):
        """This constructor sets the day name to the Date instantiation - MC 9/25/24"""
        dayName = str(dayName).lower()
        for date in self.dayOfWeek:
            if dayName == self.dayOfWeek[date]:
                dateName = self.dayOfWeek[date]
                return
        print("Error in the Date constructor: Date name not in dayOfWeek list")
    
    def insertUserData(self, userName) #SET UP DATABASE SO WE CAN HAVE USERNAME KEY FOR DICTIONARY KEY value pair
        """This function inserts a username into the username/event holder value pair - MC 9/25/24"""
        if(userName not in self.userDataDict.keys()):
            self.userDataDict[str(userName).lower()] = None
            return

    def insertEvent(self, userName, eventName): # Add event to user key value pair
        return