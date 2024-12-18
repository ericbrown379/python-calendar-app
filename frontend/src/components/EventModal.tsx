import { useState, useEffect } from 'react';
import styles from '@/styles/EventModal.module.css';
import { CalendarEvent } from '@/services/eventService';
import { PlacesAutocomplete } from '@/components/PlacesAutocomplete';
import { useRouter } from 'next/router';

interface EventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (event: Partial<CalendarEvent>) => void;
  event?: Partial<CalendarEvent>;
  mode: 'create' | 'edit';
}

interface Suggestion {
  id: number;
  name: string;
  time: string;
  explanation: string;
}

interface Attendee {
  id: number;
  username: string;
}

export default function EventModal({ isOpen, onClose, onSave, event, mode }: EventModalProps) {
  const [formData, setFormData] = useState<Partial<CalendarEvent>>({
    title: '',
    start: new Date(),
    end: new Date(),
    description: '',
    allDay: false,
    backgroundColor: '#3B82F6',
    location: '',
    notification_hours: '1',
    required_attendees: [],
    optional_attendees: []
  });

  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [attendees, setAttendees] = useState<Attendee[]>([]);
  const [locationType, setLocationType] = useState<'current' | 'address'>('current');
  const [suggestedLocations, setSuggestedLocations] = useState<string[]>([]);
  const router = useRouter();

  useEffect(() => {
    if (event) {
      setFormData({
        ...event,
        notification_hours: event.notification_hours || '1'
      });
    }
    fetchAttendees();
    if (formData.start) {
      fetchEventSuggestions(formData.start);
    }
  }, [event]);

  const fetchAttendees = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/users');
      const data = await response.json();
      setAttendees(data);
    } catch (error) {
      console.error('Error fetching attendees:', error);
    }
  };

  const fetchEventSuggestions = async (date: Date) => {
    try {
      // First check if user is authenticated
      const authResponse = await fetch('http://127.0.0.1:5001/check-auth', {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });

      if (!authResponse.ok) {
        console.error('Auth check failed:', authResponse.status);
        if (authResponse.status === 401) {
          // Handle unauthorized - maybe redirect to login
          router.push('/login');
        }
        return []; // Return empty array instead of throwing error
      }

      console.log("Fetching suggestions for date:", date);
      const response = await fetch(
        `http://127.0.0.1:5001/suggestions/event?date=${date.toISOString().split('T')[0]}`,
        {
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        }
      );

      if (!response.ok) {
        console.error('Failed to fetch suggestions:', response.status);
        return [];
      }

      const data = await response.json();
      return data.suggestions || [];
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      return [];
    }
  };

  const handleLocationTypeChange = (type: 'current' | 'address') => {
    setLocationType(type);
    if (type === 'current') {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;
        const response = await fetch(`http://localhost:5001/api/locations/nearby?lat=${latitude}&lng=${longitude}`);
        const data = await response.json();
        setSuggestedLocations(data.locations);
      });
    }
  };

  const useSuggestion = (suggestion: Suggestion) => {
    setFormData(prev => ({
      ...prev,
      title: suggestion.name,
      start: new Date(suggestion.time)
    }));
  };

  return (
    <div className={`${styles.modalOverlay} ${isOpen ? styles.show : ''}`}>
      <div className={styles.modalContent}>
        <h2>{mode === 'create' ? 'Add Event' : 'Edit Event'}</h2>
        
        <form onSubmit={(e) => {
          e.preventDefault();
          onSave(formData);
        }}>
          <div className={styles.formGroup}>
            <label htmlFor="title">Title</label>
            <input
              type="text"
              id="title"
              value={formData.title || ''}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="start">Start</label>
            <input
              type="datetime-local"
              id="start"
              value={formData.start instanceof Date ? formData.start.toISOString().slice(0, 16) : ''}
              onChange={(e) => setFormData({...formData, start: new Date(e.target.value)})}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="end">End</label>
            <input
              type="datetime-local"
              id="end"
              value={formData.end instanceof Date ? formData.end.toISOString().slice(0, 16) : ''}
              onChange={(e) => setFormData({...formData, end: new Date(e.target.value)})}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>

          <div className={styles.formGroup}>
            <label>
              <input
                type="checkbox"
                checked={formData.allDay}
                onChange={(e) => setFormData({...formData, allDay: e.target.checked})}
              />
              All Day
            </label>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="color">Color</label>
            <input
              type="color"
              id="color"
              value={formData.backgroundColor}
              onChange={(e) => setFormData({...formData, backgroundColor: e.target.value})}
            />
          </div>

          <div className={styles.formGroup}>
            <label>Location Type</label>
            <select onChange={(e) => handleLocationTypeChange(e.target.value as 'current' | 'address')}>
              <option value="current">Use Current Location</option>
              <option value="address">Enter Address</option>
            </select>

            {locationType === 'address' && (
              <PlacesAutocomplete
                onSelect={(address) => setFormData({...formData, location: address})}
              />
            )}

            {locationType === 'current' && suggestedLocations.length > 0 && (
              <select
                onChange={(e) => setFormData({...formData, location: e.target.value})}
              >
                {suggestedLocations.map((loc, idx) => (
                  <option key={idx} value={loc}>{loc}</option>
                ))}
              </select>
            )}
          </div>

          <div className={styles.formGroup}>
            <label>Required Attendees</label>
            <select
              multiple
              onChange={(e) => {
                const selected = Array.from(e.target.selectedOptions, option => Number(option.value));
                setFormData({...formData, required_attendees: selected});
              }}
            >
              {attendees.map(attendee => (
                <option key={attendee.id} value={attendee.id}>
                  {attendee.username}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup}>
            <label>Notification Hours Before Event</label>
            <select
              value={formData.notification_hours}
              onChange={(e) => setFormData({...formData, notification_hours: e.target.value})}
            >
              {[1,2,3,4,5,6,12].map(hours => (
                <option key={hours} value={hours}>{hours} hour(s)</option>
              ))}
            </select>
          </div>

          {suggestions.length > 0 && (
            <div className={styles.suggestionsSection}>
              <h3>Suggestions</h3>
              <div className={styles.suggestionsList}>
                {suggestions.map(suggestion => (
                  <div key={suggestion.id} className={styles.suggestionCard}>
                    <h4>{suggestion.name}</h4>
                    <p>{suggestion.explanation}</p>
                    <button type="button" onClick={() => useSuggestion(suggestion)}>
                      Use This
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className={styles.buttonGroup}>
            <button type="submit" className={styles.saveButton}>
              Save
            </button>
            <button type="button" onClick={onClose} className={styles.cancelButton}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 