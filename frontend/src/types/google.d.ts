declare global {
  interface Window {
    google: typeof google;
    initAutocomplete: () => void;
  }
}

interface InitAutocomplete {
  (): void;
}

export {}; 