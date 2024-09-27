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
                        FOREIGN KEY(username) REFERENCES user(username)
                    )
                    ''')
                        #START_TIME AND END_TIME stored as ##:## ex) 3:30
                        #DATE stored as 3 char of the date all lowercase ex) sun, mon, thu

        cursor.execute('''
                    Create Table If Not Exists date(
                       dateName TEXT PRIMARY KEY
                       FOREIGN KEY(username) REFERENCES user(username)
                       )
                        '''
        )
        connection.commit()
        connection.close()
        
        return
    
    def insertUser(self, inputUsername:str, inputPassword:str):
        connection =  sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                    INSERT INTO user
                        (username, password)
                        Values(?,?)
                       ''', (inputUsername, inputPassword)
                       )
        
        connection.commit()
        connection.close()
        
        return
    
    def viewUserTable():
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('''
                      SELECT * FROM user
                       ''')
        user = cursor.fetchall()
        print(user)

        connection.close()
    
    def verifyLogin(self,inputUsername:str,inputPassword:str):
        connection = sqlite3.connect('calendar.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?',(inputUsername, inputPassword))

        loginInfo = cursor.fetchone()

        if(loginInfo):
            return True
        else:
            return False
# IT WORKS!!!
myCalendar = CalendarDatabase
myCalendar.viewUserTable()