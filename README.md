# Python Calendar App

## Overview

This is a Python-based calendar application that allows users to create, manage, edit, and delete events. Users can view events on a weekly basis, with all times displayed and stored in Eastern Time (ET). The application uses Flask as the web framework and SQLAlchemy for database interactions. It also includes user authentication (login, logout, and registration).

Key features:
- Create, view, edit, and delete events.
- All events are stored and displayed in Eastern Time (ET).
- User authentication system (registration, login, and logout).
- Events are displayed in a weekly view.
- Events are stored in a SQLite database.

## Features

- **User Authentication**: Users can register, log in, and log out.
- **Event Management**: Add, edit, or delete events. Events can span over multiple hours, and times are displayed in Eastern Time (ET).
- **Time Management**: All times are handled in Eastern Time (no UTC), with the display format in 12-hour AM/PM format.
- **Weekly Calendar View**: Users can view their events for the current week.

## Installation

### 1. Clone the Repository:
```bash
git clone https://github.com/ericbrown379/python-calendar-app.git
cd python-calendar-app

### 2. Set Up the Virtual Environment (Optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

### 3. Install Dependencies:
```bash
pip install -r requirements.txt

### 4. Set Up the SQLite Database:
```bash
flask db init
flask db migrate
flask db upgrade

### 5. Run application
```flask run
The app should now be running at http://127.0.0.1:5000/.

Usage

1. Register an Account:

	•	Navigate to the /register route (e.g., http://127.0.0.1:5000/register) to create a new account.

2. Login:

	•	After registering, navigate to the /login route to log in.

3. Manage Events:

	•	Once logged in, you can view your weekly events at /week. From here, you can:
	•	Add Events: Click “Add Event” to create a new event.
	•	Edit Events: Click “Edit” next to any event to modify it.
	•	Delete Events: Click “Delete” to remove an event.

4. Logout:

	•	To log out, simply click the “Logout” button in the navigation bar.

Project Structure
├── app.py                 # Main Flask application
├── forms.py               # Flask-WTF forms for user and event input
├── models.py              # SQLAlchemy models (User, Event)
├── templates/             # HTML templates (login, register, week_view, add_event, edit_event)
├── static/                # Static files (CSS, JavaScript)
├── README.md              # This file
├── requirements.txt       # Dependencies for the app
├── venv/                  # Virtual environment (optional)
└── calendar.db            # SQLite database (automatically created after setup)


Important Notes

	•	Time Management: All event times are handled in Eastern Time (ET). The database stores event times directly in ET, and times are displayed in a 12-hour AM/PM format for user convenience.
	•	Database: The app uses SQLite for local storage. You can configure the database settings in app.py.
	•	Flask-WTF: Form handling and validation are done using Flask-WTF, ensuring that inputs like event times and user credentials are validated on the server side.

License

This project is licensed under the MIT License. See the LICENSE file for more details.

Contributing

Feel free to submit issues, fork the repository, and make a pull request if you wish to contribute. All contributions are welcome!

Repo: https://github.com/ericbrown379/python-calendar-app


