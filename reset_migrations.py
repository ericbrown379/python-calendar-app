# reset_migrations.py
from app import app, db
import os
import shutil
from sqlalchemy import text

def reset_migrations():
    print("Resetting database and migrations...")
    
    # Remove the database
    if os.path.exists('calendar.db'):
        os.remove('calendar.db')
        print("Removed existing database")

    # Remove the migrations folder
    if os.path.exists('migrations'):
        shutil.rmtree('migrations')
        print("Removed migrations folder")

    # Create new database
    with app.app_context():
        print("Creating new database...")
        db.create_all()
        
        # Clear any existing alembic version using the correct syntax
        with db.engine.connect() as connection:
            connection.execute(text('DROP TABLE IF EXISTS alembic_version'))
            connection.commit()
        
        print("Database reset complete!")

if __name__ == "__main__":
    reset_migrations()