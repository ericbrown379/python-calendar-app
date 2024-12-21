# test_db.py
from backend.app import app, db
from backend.models import User, Event
from datetime import datetime, date, time

def create_test_event(user_id):
    with app.app_context():
        try:
            print(f"Creating test event for user: {user_id}")
            
            # Format date and times as strings according to the model's requirements
            test_event = Event(
                name='Test Event',
                date=date.today().strftime('%Y-%m-%d'),  # Format as 'YYYY-MM-DD'
                start_time='09:00:00',  # Format as 'HH:MM:SS'
                end_time='10:00:00',    # Format as 'HH:MM:SS'
                description='Test Description',
                location='Test Location',
                user_id=1  # Changed to 2 for EricB's ID
            )
            
            db.session.add(test_event)
            db.session.commit()
            print(f"Successfully created test event: {test_event.name}")
            
            # Verify the event was created
            retrieved_event = Event.query.filter_by(user_id=2).order_by(Event.id.desc()).first()
            if retrieved_event:
                print(f"Retrieved event details:")
                print(f"Name: {retrieved_event.name}")
                print(f"Date: {retrieved_event.date}")
                print(f"Start Time: {retrieved_event.start_time}")
                print(f"End Time: {retrieved_event.end_time}")
                print(f"Location: {retrieved_event.location}")
                print(f"User ID: {retrieved_event.user_id}")
            else:
                print("Failed to retrieve event")
            
        except Exception as e:
            print(f"Error creating test event: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_test_event(1)  # Directly create event for user ID 2 (EricB)