import axios from 'axios';
import { EventInput } from '@fullcalendar/core';

export interface CalendarEvent {
  id?: string;
  title: string;
  start: Date | string;
  end: Date | string;
  description?: string;
  allDay?: boolean;
  backgroundColor?: string;
  location?: string;
  notification_hours?: string;
  required_attendees?: number[];
  optional_attendees?: number[];
  user_id?: number;
}

// Create axios instance with proper API URL and configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001',
  withCredentials: false,  // Changed to false to avoid CORS issues
  timeout: 15000,  // Increased timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor for auth
api.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    } catch (error) {
      console.error('Error in request interceptor:', error);
      return config;
    }
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    return Promise.reject(error);
  }
);

class EventService {
  async getAllEvents(): Promise<CalendarEvent[]> {
    try {
      const response = await api.get('/api/events');  // Added /api prefix
      if (!response.data) {
        throw new Error('No data received from server');
      }
      return response.data.map(this.transformEventFromServer);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('API Error:', {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
          config: error.config
        });
        
        // Handle specific error cases
        if (!error.response) {
          console.error('Network Error Details:', error);
          return []; // Return empty array instead of throwing
        }
        if (error.response.status === 401) {
          window.location.href = '/login';
          return [];
        }
        if (error.response.status === 404) {
          console.warn('No events found');
          return [];
        }
        
        // For other errors, return empty array and log
        console.error('Unexpected error:', error.response.data?.message);
        return [];
      }
      console.error('Non-axios error:', error);
      return [];
    }
  }

  async createEvent(event: Partial<CalendarEvent>): Promise<CalendarEvent> {
    try {
      const response = await api.post('/events', this.transformEventToServer(event));
      return this.transformEventFromServer(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('API Error:', error.response?.data || error.message);
        throw new Error(error.response?.data?.message || 'Failed to create event');
      }
      throw error;
    }
  }

  async updateEvent(event: CalendarEvent): Promise<CalendarEvent> {
    try {
      const response = await api.put(
        `/events/${event.id}`,
        this.transformEventToServer(event)
      );
      return this.transformEventFromServer(response.data);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('API Error:', error.response?.data || error.message);
        throw new Error(error.response?.data?.message || 'Failed to update event');
      }
      throw error;
    }
  }

  async deleteEvent(eventId: string): Promise<void> {
    try {
      await api.delete(`/events/${eventId}`);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('API Error:', error.response?.data || error.message);
        throw new Error(error.response?.data?.message || 'Failed to delete event');
      }
      throw error;
    }
  }

  private transformEventFromServer(event: any): CalendarEvent {
    return {
      id: String(event.id),
      title: event.title || event.name, // Handle both title and name fields
      start: new Date(event.start_time || event.start),
      end: new Date(event.end_time || event.end),
      description: event.description,
      allDay: event.all_day || event.allDay,
      backgroundColor: event.color || '#3B82F6',
      user_id: event.user_id
    };
  }

  private transformEventToServer(event: Partial<CalendarEvent>): any {
    return {
      title: event.title,
      start_time: event.start instanceof Date ? event.start.toISOString() : event.start,
      end_time: event.end instanceof Date ? event.end.toISOString() : event.end,
      description: event.description,
      all_day: event.allDay,
      color: event.backgroundColor
    };
  }
}

export const eventService = new EventService();
