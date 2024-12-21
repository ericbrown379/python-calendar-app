import axios, { AxiosError } from 'axios';
import { Event, EventSuggestion, ApiError, BlockedTime } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const ApiService = {
    // Auth endpoints
    login: async (username: string, password: string) => {
      try {
        const response = await api.post('/login', { username, password });
        return response.data;
      } catch (error) {
        throw handleApiError(error);
      }
    },

    // Event endpoints
    getWeekEvents: async () => {
        try {
          const response = await api.get<Event[]>('/week');
          console.log('API Response:', response);
          return response.data;
        } catch (error) {
          console.error('API Error:', error);
          throw handleApiError(error);
        }
    },

      // Blocked Time endpoints
  getBlockedTimes: async () => {
    try {
      const response = await api.get<BlockedTime[]>('/block_time');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

    addEvent: async (eventData: Omit<Event, 'id'>) => {
        try {
          const response = await api.post<Event>('/add_event', eventData);
          return response.data;
        } catch (error) {
          throw handleApiError(error);
        }
    },

    editEvent: async (eventId: number, eventData: Partial<Event>) => {
        try {
            const response = await api.put<Event>(`/edit_event/${eventId}`, eventData);
            return response.data;
        } catch (error) {
            throw handleApiError(error);
        }
    },

    deleteEvent: async (eventId: number) => {
        try {
            await api.delete(`/delete_event/${eventId}`);
        } catch (error) {
            throw handleApiError(error);
        }
    },
      
    // Suggestion endpoints
    getEventSuggestions: async (date: string) => {
        try {
          const response = await api.get<{ suggestions: EventSuggestion[] }>(
            `/api/suggestions/event?date=${date}`
          );
          return response.data.suggestions;
        } catch (error) {
          throw handleApiError(error);
        }
    },

    getLocationSuggestions: async (lat: number, lng: number) => {
        try {
          const response = await api.get<{ suggestions: string[] }>(
            `/api/suggestions?lat=${lat}&lng=${lng}`
          );
          return response.data.suggestions;
        } catch (error) {
          throw handleApiError(error);
        }
    },
};

function handleApiError(error: unknown): never {
    console.error('API Error Details:', error);
    
    if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        if (axiosError.response?.data) {
            throw {
                message: axiosError.response.data.error || 'Server error',
                status: axiosError.response.status
            };
        }
        if (axiosError.request) {
            throw {
                message: 'No response from server',
                status: 503
            };
        }
    }
    throw {
        message: 'Network error',
        status: 500
    };
}

export default ApiService;