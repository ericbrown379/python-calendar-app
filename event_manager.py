## event_manager.py
from flask import jsonify
from storage_manager import StorageManager
from models import Event
from dotenv import load_dotenv
import os
import requests

load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
class EventManager:
    """Manages business logic for event-related operations"""

    def __init__(self):
        """Initialize the EventManager with SQLAlchemy session."""
        self.storage_manager = StorageManager()

    def fetch_location_suggestions(self, location):
        """API endpoint to fetch location suggestions"""
        lat, lng = map(float, location.split(","))
        suggestions = self.suggest_locations((lat, lng))
        return jsonify({"suggestions": suggestions})

    def get_coordinates(self, address):
        """Get latitude and longitude from an address using OpenCage API."""
        url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={OPENCAGE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get('results')
            if results:
                latitude = results[0]['geometry']['lat']
                longitude = results[0]['geometry']['lng']
                return latitude, longitude
        return None
    
    def suggest_locations(self, user_location, event_type=None, distance=2000):
        """Suggest locations using Google Places API based on user location and event type"""
        place_type = event_type if event_type else 'restaurant'
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={user_location[0]},{user_location[1]}&radius={distance}&type={place_type}&key={GOOGLE_PLACES_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            places = response.json().get('results', [])
            return [{
                'name': place.get('name', ''),
                'vicinity': place.get('vicinity', 'No address available')
            } for place in places]
        return []
    
    def calculate_midpoint(self, coordinates):
        """Calculate midpoint for multiple coordinates."""
        latitudes = [coord[0] for coord in coordinates]
        longitudes = [coord[1] for coord in coordinates]
        return sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)


    def add_event(self, name, date, start_time, end_time, location, description, user_id, required_attendees=None, optional_attendees=None):
        """Add a new event using SQLAlchemy."""
        event = Event(
            name=name,
            date=date,
            start_time=start_time,
            end_time=end_time,
            location=location,  # Add location field
            description=description,
            user_id=user_id
        )
        
        # Handle attendees if provided
        if required_attendees:
            event.required_attendees = required_attendees
        if optional_attendees:
            event.optional_attendees = optional_attendees
            
        self.storage_manager.insert_event(event)
        return event

    def edit_event(self, event_id, name=None, date=None, start_time=None, end_time=None, location=None, description=None):
        """Edit an existing event using SQLAlchemy."""
        event = self.storage_manager.retrieve_event(event_id)
        if event:
            if name is not None:
                event.name = name
            if date is not None:
                event.date = date
            if start_time is not None:
                event.start_time = start_time
            if end_time is not None:
                event.end_time = end_time
            if location is not None:
                event.location = location
            if description is not None:
                event.description = description
            
            self.storage_manager.update_event(event)
            return event
        return None

    def delete_event(self, event_id):
        """Delete an event using SQLAlchemy."""
        self.storage_manager.delete_event(event_id)

    def get_events_by_date(self, user_id, date):
        """Get all events for a specific date for a user."""
        return self.storage_manager.retrieve_events_by_date(user_id, date)

    def search_events(self, user_id, keyword=None, date=None):
        """Search for events by keyword or date."""
        if date:
            return self.get_events_by_date(user_id, date)
        elif keyword:
            all_events = self.storage_manager.retrieve_events(user_id)
            return [event for event in all_events if keyword.lower() in event.name.lower() or keyword.lower() in event.description.lower()]
        return []