# setup_database.py
from app import app, db
import os
import shutil
from sqlalchemy import text, inspect
from flask_migrate import init, migrate, upgrade, stamp
from models import User, Event, Feedback, EventSuggestion, UserPreferences

def setup_database():
    print("Starting complete database setup...")
    
    with app.app_context():
        try:
            # 1. Clean up existing files
            if os.path.exists('calendar.db'):
                os.remove('calendar.db')
                print("Removed existing database")
            
            if os.path.exists('migrations'):
                shutil.rmtree('migrations')
                print("Removed migrations folder")
            
            # 2. Create fresh database
            db.create_all()
            print("Created new database tables")
            
            # 3. Initialize migrations
            os.system('flask db init')
            print("Initialized migrations")
            
            # 4. Create and apply initial migration
            os.system('flask db migrate -m "initial migration"')
            os.system('flask db upgrade')
            print("Applied initial migration")
            
            # 5. Verify database setup
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("\nVerifying database tables:")
            for table in tables:
                print(f"- {table}")
                columns = inspector.get_columns(table)
                for column in columns:
                    print(f"  * {column['name']}: {column['type']}")
            
            print("\nDatabase setup completed successfully!")
            
        except Exception as e:
            print(f"Error during setup: {str(e)}")
            return False
        
        return True

def verify_database():
    with app.app_context():
        try:
            # Get inspector
            inspector = inspect(db.engine)
            
            # Get all table names
            tables = inspector.get_table_names()
            print("\nCurrent database tables:", tables)
            
            # Define required tables
            required_tables = {'user', 'event', 'feedback', 'event_suggestion', 'user_preferences',
                             'required_attendees', 'optional_attendees', 'alembic_version'}
            
            # Check for missing tables
            missing_tables = required_tables - set(tables)
            if missing_tables:
                print(f"\nMissing tables: {missing_tables}")
                return False
                
            print("\nAll required tables are present!")
            
            # Verify table structures
            print("\nVerifying table structures:")
            for table in tables:
                print(f"\nTable: {table}")
                columns = inspector.get_columns(table)
                print("Columns:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            
            return True
            
        except Exception as e:
            print(f"\nError verifying database: {str(e)}")
            return False

def reset_alembic():
    with app.app_context():
        try:
            # Remove existing alembic version
            with db.engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
                conn.commit()
            print("Reset alembic version table")
            return True
        except Exception as e:
            print(f"Error resetting alembic: {str(e)}")
            return False

if __name__ == "__main__":
    os.environ['FLASK_APP'] = 'app.py'
    
    # First reset alembic
    if reset_alembic():
        # Then setup database
        if setup_database():
            # Finally verify
            if verify_database():
                print("\nComplete database setup and verification successful!")
            else:
                print("\nDatabase verification failed!")
        else:
            print("\nDatabase setup failed!")
    else:
        print("\nFailed to reset alembic!")