import requests
from backend.event_manager import EventManager

# URL for your Flask app's event creation route
# url = "http://127.0.0.1:5000/add_event"

# # Sample data to add 100 events
# for i in range(1, 101):  # Change range to 1000 if needed
#     event_data = {
#         "name": f"Event {i}",
#         "date": "2024-09-30",  # Change the date dynamically if needed
#         "start_time": "09:00 AM",
#         "end_time": "10:00 AM",
#         "description": f"Description for event {i}",
#         "submit": "Submit"
#     }

#     # Send a POST request to add the event
#     response = requests.post(url, data=event_data)

#     # Print the response to verify if the event is added
#     print(f"Added Event {i}, Status Code: {response.status_code}")
# Test the get_coordinates function
# def test_get_coordinates():
#     # Initialize EventManager
#     event_manager = EventManager()

#     # Test with a known address
#     address = "1600 Amphitheatre Parkway, Mountain View, CA"
#     coordinates = event_manager.get_coordinates(address)
    
#     if coordinates:
#         print(f"Coordinates for '{address}': {coordinates}")
#     else:
#         print("Failed to get coordinates. Check API key or network connection.")


def test_suggest_locations():
    # Initialize EventManager
    event_manager = EventManager()
    
    # Define a known user location (latitude, longitude)
    user_location = (37.4217636, -122.084614)  # Example: Mountain View, CA
    
    # Define an optional event type (e.g., 'park', 'museum', etc.)
    event_type = "restaurant"  # Change this to test different types
    
    # Call suggest_locations with a sample location
    suggestions = event_manager.suggest_locations(user_location, event_type=event_type)
    
    # Print results
    if suggestions:
        print(f"Suggestions for '{event_type}' near {user_location}:")
        for name, vicinity in suggestions:
            print(f" - {name}, located at {vicinity}")
    else:
        print("No suggestions found or API request failed.")

#     url = "http://127.0.0.1:5000/add_event"

# # Test cases with forbidden characters in the name or description
# forbidden_chars_test = [
#     {"name": "Event #1", "description": "Description with #"},
#     {"name": "Event $2", "description": "Description with $"},
#     {"name": "Event ^3", "description": "Description with ^"},
#     {"name": "Event 4", "description": "Description with forbidden characters like @#$%^"},
# ]

# for event in forbidden_chars_test:
#     event_data = {
#         "name": event["name"],
#         "date": "2024-09-30",
#         "start_time": "10:00 AM",
#         "end_time": "11:00 AM",
#         "description": event["description"],
#         "submit": "Submit"
#     }

#     response = requests.post(url, data=event_data)

#     # Check if the response indicates a validation error
#     if response.status_code == 200 and "forbidden characters" in response.text.lower():
#         print(f"Validation error correctly detected for event: {event['name']}")
#     else:
#         print(f"Added Event with name '{event['name']}', Status Code: {response.status_code}")
        
if __name__ == "__main__":
    test_suggest_locations()