import { useEffect, useRef, useState } from 'react';
import styles from '@/styles/PlacesAutocomplete.module.css';

declare global {
  interface Window {
    initAutocomplete: () => void;
  }
}

interface PlacesAutocompleteProps {
  onSelect: (address: string) => void;
}

export function PlacesAutocomplete({ onSelect }: PlacesAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [autocomplete, setAutocomplete] = useState<google.maps.places.Autocomplete | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error('Google Maps Script Error:', error);
      setError('Failed to load location services');
    };

    window.initAutocomplete = () => {
      try {
        if (!inputRef.current) return;

        const autocompleteInstance = new google.maps.places.Autocomplete(inputRef.current, {
          types: ['establishment', 'geocode'],
          componentRestrictions: { country: 'us' },
          fields: ['address_components', 'geometry', 'name', 'formatted_address']
        });

        autocompleteInstance.addListener('place_changed', () => {
          try {
            const place = autocompleteInstance.getPlace();
            if (place.formatted_address) {
              onSelect(place.formatted_address);
            }
          } catch (e) {
            console.error('Error handling place selection:', e);
          }
        });

        setAutocomplete(autocompleteInstance);
      } catch (e) {
        console.error('Error initializing autocomplete:', e);
        setError('Failed to initialize location search');
      }
    };

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY}&libraries=places&callback=initAutocomplete`;
    script.async = true;
    script.defer = true;
    script.onerror = () => handleError(new ErrorEvent('error'));
    document.head.appendChild(script);

    return () => {
      if (autocomplete) {
        google.maps.event.clearInstanceListeners(autocomplete);
      }
      window.initAutocomplete = () => {};
      const scriptElement = document.querySelector(`script[src*="maps.googleapis.com"]`);
      if (scriptElement) {
        scriptElement.remove();
      }
    };
  }, [onSelect]);

  return (
    <div className={styles.container}>
      {error && <div className={styles.error}>{error}</div>}
      <input
        ref={inputRef}
        type="text"
        className={styles.input}
        placeholder="Enter location"
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
          }
        }}
      />
    </div>
  );
} 