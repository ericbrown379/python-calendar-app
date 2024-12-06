# view_accounts.py
from app import app, db
from models import User

def view_accounts():
    with app.app_context():
        try:
            print("\nListing all accounts in database:")
            print("-" * 50)
            
            users = User.query.all()
            if not users:
                print("No accounts found in database.")
                return

            for user in users:
                print(f"ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Verified: {user.is_verified}")
                print(f"Address: {user.address}")
                print(f"Notifications Enabled: {user.notifications_enabled}")
                print(f"Notification Hours: {user.notification_hours}")
                print("-" * 50)

            print(f"\nTotal accounts: {len(users)}")
            
        except Exception as e:
            print(f"Error viewing accounts: {str(e)}")

if __name__ == "__main__":
    view_accounts()