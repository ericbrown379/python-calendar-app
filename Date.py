from Event import Event

class Date:
    # 2D array storing available time intervals (e.g., [[1, 2], [4, 9]])
    dateName = ""
    dayOfWeek = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]  # Set of valid days
    userDataDict = {}


    def __init__(self, dayName:str):
        """ This constructor sets the day name to the Date instantiation - MC 9/25/24 """
        self.userDataDict = {}

        dayName = str(dayName).lower()
        for date in self.dayOfWeek:
            if dayName == date:  
                self.dateName = date  #
                return
        print("Error in the Date constructor: Date name not in dayOfWeek list")
    

    def insertUserData(self, userName:str): #SET UP DATABASE SO WE CAN HAVE USERNAME KEY FOR DICTIONARY KEY value pair
        """This function inserts a username into the username/event holder value pair - MC 9/25/24"""
        if(not self.checkIfUserExists(userName)):
            self.userDataDict[str(userName).lower()] = []
            return
        else:
            print("The user already exists in the database")


    def insertEvent(self, userName:str, eventName:Event): # Add event to user key value pair
        self.insertUserData(userName)
        if(isinstance(eventName, Event)):
            self.userDataDict[userName].append(eventName)
            return
        else:
            print("The event has an error being inputted")
    

    def checkIfUserExists(self, userName:str):
        if(userName in self.userDataDict.keys()):
            return True
        else:
            return False
        
    def findTimeIntersection(): #This function should return a list of all the times that everyone is available
        return