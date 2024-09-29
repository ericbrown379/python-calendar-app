import sqlite3
from Event import Event

class StorageManager:
    """Handles SQLite database interactions for event storage and retrieval."""

    def __init__(self):
        """Initialize the SQLite database connection and create tables if necessary."""
        self.connection = sqlite3.connect('calendar.db')
        self.cursor = self.connection.cursor()

        # Create user table (assuming you will handle users, as mentioned in your requirements)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')

        # Create event table (with foreign key to the user)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS event(
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                eventName TEXT NOT NULL,
                startTime TEXT NOT NULL, 
                endTime TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        ''')

        self.connection.commit()

    def close_connection(self):
        """Closes the database connection."""
        self.connection.close()

    def insert_event(self, event: Event, user_id: int):
        """
        Insert an event into the database.
        :param event: Event object to insert.
        :param user_id: ID of the user who owns the event.
        :return: None
        """
        self.cursor.execute('''
            INSERT INTO event (eventName, startTime, endTime, date, description, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event.name, event.start_time, event.end_time, event.date, event.description, user_id))
        self.connection.commit()

    def retrieve_event(self, event_id: int) -> Event:
        """
        Retrieve a single event by event_id.
        :param event_id: ID of the event to retrieve.
        :return: Event object if found, None if not found.
        """
        self.cursor.execute('SELECT * FROM event WHERE event_id = ?', (event_id,))
        row = self.cursor.fetchone()

        if row:
            return Event(row[0], row[1], row[4], row[2], row[3], row[5])
        return None

    def retrieve_events_by_date(self, user_id: int, date: str):
        """
        Retrieve all events for a user on a specific date.
        :param user_id: ID of the user.
        :param date: Date to retrieve events for.
        :return: List of Event objects.
        """
        self.cursor.execute('''
            SELECT * FROM event 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))

        rows = self.cursor.fetchall()
        events = [Event(row[0], row[1], row[4], row[2], row[3], row[5]) for row in rows]
        return events

    def retrieve_events(self, user_id: int):
        """
        Retrieve all events for a user.
        :param user_id: ID of the user.
        :return: List of Event objects.
        """
        self.cursor.execute('''
            SELECT * FROM event WHERE user_id = ?
        ''', (user_id,))

        rows = self.cursor.fetchall()
        events = [Event(row[0], row[1], row[4], row[2], row[3], row[5]) for row in rows]
        return events

    def update_event(self, event: Event):
        """
        Update an event's details in the database.
        :param event: Updated Event object.
        :return: None
        """
        self.cursor.execute('''
            UPDATE event
            SET eventName = ?, startTime = ?, endTime = ?, date = ?, description = ?
            WHERE event_id = ?
        ''', (event.name, event.start_time, event.end_time, event.date, event.description, event.event_id))
        self.connection.commit()

    def delete_event(self, event_id: int):
        """
        Delete an event from the database by event_id.
        :param event_id: ID of the event to delete.
        :return: None
        """
        self.cursor.execute('DELETE FROM event WHERE event_id = ?', (event_id,))
        self.connection.commit()

    def get_next_event_id(self):
        """
        Get the next available event ID.
        (Only needed if you're manually setting event IDs outside the database)
        :return: Next available event_id.
        """
        self.cursor.execute('SELECT MAX(event_id) FROM event')
        result = self.cursor.fetchone()
        return result[0] + 1 if result and result[0] else 1

    def __del__(self):
        """Destructor to close the connection when StorageManager is deleted."""
        self.close_connection()