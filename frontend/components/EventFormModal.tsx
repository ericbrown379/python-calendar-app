'use client';

import { useState, useEffect } from 'react';
import styles from '@/styles/eventModal.module.css';
import { FaTimes, FaMapMarkerAlt, FaClock, FaUsers, FaBell } from 'react-icons/fa';
import Script from 'next/script';

interface AutocompleteOptions {
  types?: string[];
  componentRestrictions?: { country: string };
  fields?: string[];
}

declare global {
  interface Window {
    google: {
      maps: {
        places: {
          Autocomplete: new (
            input: HTMLInputElement,
            opts?: AutocompleteOptions
          ) => {
            addListener: (event: string, handler: () => void) => void;
            getPlace: () => { geometry?: { location: { lat: () => number; lng: () => number } } };
          };
        };
      };
    };
  }
}

interface GoogleAutocomplete {
  addListener: (event: string, handler: () => void) => void;
  getPlace: () => { geometry?: { location: { lat: () => number; lng: () => number } } };
}

let autocomplete: GoogleAutocomplete | null = null;

interface EventFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDate?: Date;
  selectedTime?: string;
}

interface LocationSuggestion {
  name: string;
  vicinity: string;
  place_id?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
}

export default function EventFormModal({ isOpen, onClose, selectedDate, selectedTime }: EventFormModalProps) {
  const [activeTab, setActiveTab] = useState('details');
  const [formData, setFormData] = useState({
    name: '',
    date: selectedDate?.toISOString().split('T')[0] || '',
    startTime: selectedTime || '',
    endTime: '',
    location: '',
    description: '',
    requiredAttendees: [],
    optionalAttendees: [],
    notificationHours: '1'
  });

  const [locationSuggestions, setLocationSuggestions] = useState<LocationSuggestion[]>([]);
  const [isSearchingLocation, setIsSearchingLocation] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<{
    required: number[];
    optional: number[];
  }>({
    required: [],
    optional: []
  });

  const [users, setUsers] = useState<User[]>([]);
  const [locationType, setLocationType] = useState<'current' | 'address'>('address');
  const [addressInput, setAddressInput] = useState('');

  useEffect(() => {
    // Fetch users for attendee selection
    const fetchUsers = async () => {
      try {
        const response = await fetch('/api/users');
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };
    fetchUsers();
  }, []);

  // Add notification settings
  const notificationOptions = [
    { value: '0', label: 'At time of event' },
    { value: '0.5', label: '30 minutes before' },
    { value: '1', label: '1 hour before' },
    { value: '24', label: '1 day before' },
  ];

  // Initialize Google Places Autocomplete
  const initializeAutocomplete = (input: HTMLInputElement) => {
    if (window.google && input) {
      autocomplete = new window.google.maps.places.Autocomplete(input, {
        types: ['establishment', 'geocode'],
        componentRestrictions: { country: 'us' },
        fields: ['address_components', 'geometry', 'name', 'formatted_address']
      });

      autocomplete.addListener('place_changed', () => {
        const place = autocomplete!.getPlace();
        if (place.geometry) {
          fetchSuggestedLocations(
            place.geometry.location.lat(),
            place.geometry.location.lng()
          );
        }
      });
    }
  };

  // Get current location
  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      setIsSearchingLocation(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          fetchSuggestedLocations(
            position.coords.latitude,
            position.coords.longitude
          );
        },
        (error) => {
          console.error("Geolocation error:", error);
          setIsSearchingLocation(false);
        }
      );
    }
  };

  // Fetch location suggestions
  const fetchSuggestedLocations = async (lat: number, lng: number) => {
    try {
      const response = await fetch(`/api/suggestions?lat=${lat}&lng=${lng}`);
      const data = await response.json();
      setLocationSuggestions(data.suggestions);
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setIsSearchingLocation(false);
    }
  };

  // Handle location selection
  const handleLocationSelect = (location: LocationSuggestion) => {
    setFormData({
      ...formData,
      location: location.name
    });
    setLocationSuggestions([]);
  };

  // Handle attendee selection
  const toggleAttendee = (userId: number, type: 'required' | 'optional') => {
    setSelectedUsers(prev => {
      const newUsers = { ...prev };
      const array = newUsers[type];
      const index = array.indexOf(userId);
      
      if (index === -1) {
        newUsers[type] = [...array, userId];
      } else {
        newUsers[type] = array.filter(id => id !== userId);
      }
      
      return newUsers;
    });
  };

  // Update the location tab content
  const LocationTab = () => (
    <div className={styles.locationSection}>
      <div className={styles.locationTypeSelect}>
        <select
          value={locationType}
          onChange={(e) => setLocationType(e.target.value as 'current' | 'address')}
          className={styles.select}
        >
          <option value="current">Use Current Location</option>
          <option value="address">Enter Address</option>
        </select>
      </div>

      {locationType === 'address' ? (
        <div className={styles.searchBox}>
          <input
            type="text"
            placeholder="Search for a location..."
            value={addressInput}
            onChange={(e) => setAddressInput(e.target.value)}
            className={styles.searchInput}
            ref={(input) => {
              if (input && !autocomplete) {
                initializeAutocomplete(input);
              }
            }}
          />
        </div>
      ) : (
        <button
          type="button"
          onClick={getCurrentLocation}
          className={styles.button}
          disabled={isSearchingLocation}
        >
          Get Nearby Locations
        </button>
      )}

      {isSearchingLocation && <div className={styles.spinner}>Searching...</div>}

      <div className={styles.suggestionsList}>
        {locationSuggestions.map((location, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handleLocationSelect(location)}
            className={styles.suggestionItem}
          >
            <strong>{location.name}</strong>
            <span>{location.vicinity}</span>
          </button>
        ))}
      </div>
    </div>
  );

  // Update the attendees tab content
  const AttendeesTab = () => (
    <div className={styles.attendeesSection}>
      <div className={styles.attendeeGroup}>
        <h3>Required Attendees</h3>
        <div className={styles.userList}>
          {users.map(user => (
            <div key={user.id} className={styles.userItem}>
              <label>
                <input
                  type="checkbox"
                  checked={selectedUsers.required.includes(user.id)}
                  onChange={() => toggleAttendee(user.id, 'required')}
                />
                {user.username}
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.attendeeGroup}>
        <h3>Optional Attendees</h3>
        <div className={styles.userList}>
          {users.map(user => (
            <div key={user.id} className={styles.userItem}>
              <label>
                <input
                  type="checkbox"
                  checked={selectedUsers.optional.includes(user.id)}
                  onChange={() => toggleAttendee(user.id, 'optional')}
                />
                {user.username}
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Add notification settings to the details tab
  const NotificationSettings = () => (
    <div className={styles.formGroup}>
      <label>
        <FaBell className={styles.icon} />
        Notification
      </label>
      <select
        value={formData.notificationHours}
        onChange={(e) => setFormData({...formData, notificationHours: e.target.value})}
        className={styles.select}
      >
        {notificationOptions.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        onClose();
        // Trigger calendar refresh
      }
    } catch (error) {
      console.error('Error creating event:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <Script
        src={`https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY}&libraries=places`}
        strategy="lazyOnload"
      />
      <div className={styles.modalOverlay}>
        <div className={styles.modal}>
          <div className={styles.modalHeader}>
            <h2>Add New Event</h2>
            <button onClick={onClose} className={styles.closeButton}>
              <FaTimes />
            </button>
          </div>

          <div className={styles.modalTabs}>
            <button 
              className={`${styles.tabButton} ${activeTab === 'details' ? styles.active : ''}`}
              onClick={() => setActiveTab('details')}
            >
              <FaClock /> Details
            </button>
            <button 
              className={`${styles.tabButton} ${activeTab === 'location' ? styles.active : ''}`}
              onClick={() => setActiveTab('location')}
            >
              <FaMapMarkerAlt /> Location
            </button>
            <button 
              className={`${styles.tabButton} ${activeTab === 'attendees' ? styles.active : ''}`}
              onClick={() => setActiveTab('attendees')}
            >
              <FaUsers /> Attendees
            </button>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={`${styles.tabContent} ${activeTab === 'details' ? styles.active : ''}`}>
              <div className={styles.formGroup}>
                <label>Event Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Date</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Start Time</label>
                  <input
                    type="time"
                    value={formData.startTime}
                    onChange={(e) => setFormData({...formData, startTime: e.target.value})}
                    required
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>End Time</label>
                  <input
                    type="time"
                    value={formData.endTime}
                    onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div className={styles.formGroup}>
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                />
              </div>
              <NotificationSettings />
            </div>

            <div className={`${styles.tabContent} ${activeTab === 'location' ? styles.active : ''}`}>
              <LocationTab />
            </div>

            <div className={`${styles.tabContent} ${activeTab === 'attendees' ? styles.active : ''}`}>
              <AttendeesTab />
            </div>

            <div className={styles.modalFooter}>
              <button type="submit" className={styles.submitButton}>
                Create Event
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
} 