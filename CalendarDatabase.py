import sqlite3

#when using this class do 'import as cDB' 
class CalendarDatabase:


    def __init__(self):
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
                            FOREIGN KEY(username) REFERENCES user(username),
                            FOREIGN KEY(eventName) REFERENCES event(eventName)
                      )
                   ''')
        connection.commit()
        connection.close()
    

    def insertUser(self, inputUsername:str, inputPassword:str):
        connection =  sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                        INSERT INTO user
                            (username, password)
                            Values(?,?)''', (inputUsername, inputPassword)
                      )
        
        connection.commit()
        connection.close()
        return
    

    def insertEvent(self, inputName:str, inputStart:str, inputEnd:str, inputDate:str):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                        INSERT INTO event
                            (eventName, startTime, endTime, date)
                            Values(?,?,?,?)''',(inputName,inputStart, inputEnd, inputDate)
                      )
        
        connection.commit()
        connection.close()
        return
        
    
    def retrieveUser(self, inputUsername:str):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM user WHERE username = ?',(inputUsername))

        user = cursor.fetchone()
        if(user):
            return user
        else:
            print("User does not exist")
            return False


    def retrieveAllUsernames(self):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute("SELECT username FROM user")
        allUsernames = cursor.fetchall()

        connection.close()
        return allUsernames


    def viewUserTable(self):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                       SELECT * FROM user
                       '''
                      )
        user = cursor.fetchall()
        print(user)

        connection.close()
    

    def viewEventTable(self):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                       SELECT * FROM event
                       '''
                      )
        user = cursor.fetchall()
        print(user)

        connection.close()
        return


    def viewDateTable(self):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                       SELECT * FROM date
                       '''
                      )
        user = cursor.fetchall()
        print(user)

        connection.close()
        return


    def verifyLogin(self,inputUsername:str,inputPassword:str):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?',(inputUsername, inputPassword))

        loginInfo = cursor.fetchone()

        connection.close()

        if(loginInfo):
            return True
        else:
            return False
        
    
    def retrieveEventsByDate(self,insertDateName:str):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()


        cursor.execute("""
                         SELECT eventName, startTime, endTime
                            FROM event
                            WHERE date = ?
                       
                       """,(insertDateName,)
                      )
        eventsByDate = cursor.fetchall()
        connection.close()

        if(eventsByDate):
            return eventsByDate
        else:
            print("Incorrect date name given")
            return False



myCalendar = CalendarDatabase
