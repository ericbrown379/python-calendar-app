# init_db.py
from backend.app import app, db
from backend.models import User, Event, Feedback, EventSuggestion, UserPreferences

def init_database():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        # Verify tables were created
        engine = db.engine
        inspector = db.inspect(engine)
        tables = inspector.get_table_names()
        print("\nCreated tables:")
        for table in tables:
            print(f"- {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  * {column['name']}: {column['type']}")

if __name__ == "__main__":
    init_database()
    print("\nDatabase initialized successfully!")