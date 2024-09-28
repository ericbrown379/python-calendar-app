import sqlite3

#when using this class do 'import as cDB' 
class CalendarDatabase:


    def __init__(self):

        try:
            #Connects to SQLite db
            connection =  sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            #cursor cnnects to the db to execute SQL cmds
            cursor.execute('''
                            Create Table If Not Exists user(
                                username TEXT PRIMARY KEY,
                                password TEXT NOT NULL
                        )
                    ''')

            cursor.execute('''
                            Create Table If Not Exists event(
                                eventName TEXT PRIMARY KEY,
                                startTime TEXT NOT NULL, 
                                endTime TEXT NOT NULL,
                                date TEXT NOT NULL UNIQUE
                        )
                    ''')
                            #START_TIME AND END_TIME stored as ##:## ex) 3:30
                            #DATE stored as 3 char of the date all lowercase ex) sun, mon, thu

            cursor.execute('''
                            Create Table If Not Exists date(
                                dateName TEXT PRIMARY KEY,
                                username TEXT,
                                eventName TEXT,
                                FOREIGN KEY(username) REFERENCES user(username),
                                FOREIGN KEY(eventName) REFERENCES event(eventName)
                        )
                    ''')
            connection.commit()
        except sqlite3.Error as Error:
            print("An error occured while intializing CalendarDatabase: " + Error)
        finally:
            connection.close()


    def insertUser(self, inputUsername:str, inputPassword:str):
        try:
            connection =  sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('''
                            INSERT INTO user
                                (username, password)
                                Values(?,?)''', (inputUsername, inputPassword)
                        )
            
            connection.commit()
        except sqlite3.Error as Error:
            print("Error while inserting user into database: " + Error)
        finally:
            connection.close()
            return
    

    def insertEvent(self, inputName:str, inputStart:str, inputEnd:str, inputDate:str):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('''
                            INSERT INTO event
                                (eventName, startTime, endTime, date)
                                Values(?,?,?,?)''',(inputName,inputStart, inputEnd, inputDate)
                        )
            
            connection.commit()
        except sqlite3.Error as Error:
            print("Error while inserting event into database: " + Error)
        finally:
            connection.close()
            return
        
    
    def retrieveUser(self, inputUsername:str):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM user WHERE username = ?',(inputUsername,))

            user = cursor.fetchone()
            connection.close()
            if(user):
                return user
            else:
                print("User does not exist")
        except sqlite3.Error as Error:
                print("Error while retrieving user data from database: " + Error)
        finally:
                return
                


    def retrieveAllUsernames(self):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute("SELECT username FROM user")
            allUsernames = cursor.fetchall()

            connection.close()
            return allUsernames
        except sqlite3.Error as Error:
            print("Error with retrieving all usernames from database: " + Error)
        finally:
            return

    def viewUserTable(self):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('''
                        SELECT * FROM user
                        '''
                        )
            user = cursor.fetchall()
            print(user)
        except sqlite3.Error as Error:
            print("Error with viewing user tables from database " + Error)
        finally:
            connection.close()
            return
    

    def viewEventTable(self):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('''
                        SELECT * FROM event
                        '''
                        )
            user = cursor.fetchall()
            print(user)
        except sqlite3.Error as Error:
            print("Error with viewing event tables from database: " + Error)
        finally: 
            connection.close()
            return


    def viewDateTable(self):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('''
                        SELECT * FROM date
                        '''
                        )
            user = cursor.fetchall()
            print(user)
        except sqlite3.Error as Error:
            print("Error with viewing date tables from database: " + Error)
            connection.close()
            return


    def verifyLogin(self,inputUsername:str,inputPassword:str) -> bool:
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?',(inputUsername, inputPassword))

            loginInfo = cursor.fetchone()

            connection.close()

            if(loginInfo):
                return True
            else:
                return False
        except sqlite3.Error as Error:
            print("Error with verifying login in database: " + Error)
        finally:
            return
        
    
    def retrieveEventsByDate(self,insertDateName:str):
        try:
            connection = sqlite3.connect('calendar.db')
            cursor = connection.cursor()


            cursor.execute("""
                            SELECT eventName, startTime, endTime
                                FROM event
                                WHERE date = ?
                        
                        """,(insertDateName,)
                        )
            eventsByDate = cursor.fetchall()

            if(eventsByDate):
                return eventsByDate
            else:
                print("Incorrect date name given")
                return False
        except sqlite3.Error as Error:
            print("Error retrieving events by date from database: " + Error)
        finally:
            connection.close()
            return


myCalendar = CalendarDatabase
