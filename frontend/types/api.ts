export interface User {
    id: number;
    username: string;
    email: string;
    notifications_enabled: boolean;
    notification_hours: number;
  }
  
  export interface Event {
    id: number;
    name: string;
    date: string;
    start_time: string;
    end_time: string;
    location: string;
    description?: string;
    user_id: number;
  }
  
  export interface BlockedTime {
    id: number;
    user_id: number;
    start_time: string;
    end_time: string;
    recurring: 'none' | 'daily' | 'weekly';
    description?: string;
  }
  
  export interface EventSuggestion {
    id: number;
    name: string;
    time: string;
    explanation: string;
    score: number;
  }
  
  export interface ApiError {
    error: string;
  }