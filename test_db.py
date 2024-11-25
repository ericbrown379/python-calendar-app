# test_db.py
from app import app, db
from models import User, Event
from datetime import datetime, date

def test_database():
    with app.app_context():
        try:
            print("Testing database operations...")
            
            # 1. Create a test user
            test_user = User(
                username='test_user',
                email='test@example.com'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("Created test user")
            
            # 2. Create a test event
            test_event = Event(
                name='Test Event',
                date=date.today().strftime('%Y-%m-%d'),
                start_time='09:00:00',
                end_time='10:00:00',
                description='Test Description',
                user_id=test_user.id
            )
            db.session.add(test_event)
            db.session.commit()
            print("Created test event")
            
            # 3. Verify we can retrieve the event
            retrieved_event = Event.query.filter_by(user_id=test_user.id).first()
            if retrieved_event:
                print(f"Successfully retrieved event: {retrieved_event.name}")
            else:
                print("Failed to retrieve event")
            
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"Error during test: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    test_database()