class Date:
    # 2D array storing available time intervals (e.g., [[1, 2], [4, 9]])
    userAvailableTime = []
    dayOfWeek = {"sun", "mon", "tue", "wed", "thu", "fri", "sat"}  # Set of valid days
    day = ""
    
    def __init__(self, inputDay, time):
        # Convert input day to lowercase and trim any extra spaces
        inputDay = inputDay.lower().strip()
        
        # Check if the input day is in dayOfWeek
        if inputDay in self.dayOfWeek:
            self.day = inputDay
        else:
            isDay = False
            while not isDay:
                # Prompt user until they provide a valid day
                inputDay = input("Please enter a valid day (e.g., wed or fri): ").lower().strip()
                if inputDay in self.dayOfWeek:
                    self.day = inputDay
                    isDay = True
        
        # Store the time (time handling logic needs to be defined)
        self.time = time
