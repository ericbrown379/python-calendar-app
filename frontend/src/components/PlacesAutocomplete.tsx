import { useEffect, useRef, useState } from 'react';
import styles from '@/styles/PlacesAutocomplete.module.css';

declare global {
  interface Window {
    initAutocomplete: () => void;
    google: any;
  }
}

interface PlacesAutocompleteProps {
  onSelect: (address: string) => void;
}

export function PlacesAutocomplete({ onSelect }: PlacesAutocompleteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isScriptLoaded, setIsScriptLoaded] = useState(false);
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);

  useEffect(() => {
    // Check if the script is already loaded
    if (window.google && window.google.maps && window.google.maps.places) {
      setIsScriptLoaded(true);
      initializeAutocomplete();
      return;
    }

    const handleError = (error: ErrorEvent) => {
      console.error('Google Maps Script Error:', error);
      setError('Failed to load location services');
    };

    window.initAutocomplete = () => {
      setIsScriptLoaded(true);
      initializeAutocomplete();
    };

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_PLACES_API_KEY}&libraries=places&callback=initAutocomplete`;
    script.async = true;
    script.defer = true;
    script.onerror = () => handleError(new ErrorEvent('error'));
    document.head.appendChild(script);

    return () => {
      if (autocompleteRef.current) {
        google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }
      const scriptElement = document.querySelector(`script[src*="maps.googleapis.com"]`);
      if (scriptElement) {
        scriptElement.remove();
      }
    };
  }, []);

  const initializeAutocomplete = () => {
    if (!inputRef.current || !window.google) return;

    try {
      autocompleteRef.current = new window.google.maps.places.Autocomplete(inputRef.current, {
        types: ['establishment', 'geocode'],
        componentRestrictions: { country: 'us' },
        fields: ['address_components', 'geometry', 'name', 'formatted_address']
      });

      autocompleteRef.current.addListener('place_changed', () => {
        try {
          const place = autocompleteRef.current?.getPlace();
          if (place?.formatted_address) {
            setInputValue(place.formatted_address);
            onSelect(place.formatted_address);
          }
        } catch (e) {
          console.error('Error handling place selection:', e);
          setError('Error selecting location');
        }
      });
    } catch (e) {
      console.error('Error initializing autocomplete:', e);
      setError('Failed to initialize location search');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    // If we're typing numbers, don't block the input
    if (/^\d*$/.test(value)) {
      onSelect(value);
    }
  };

  return (
    <div className={styles.container}>
      {error && <div className={styles.error}>{error}</div>}
      <input
        ref={inputRef}
        type="text"
        className={styles.input}
        placeholder="Enter location"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
          }
        }}
        autoComplete="off"
      />
    </div>
  );
} 