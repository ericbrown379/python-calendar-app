export interface Event {
    id: string;
    title: string;
    start: string;
    end: string;
    description?: string;
    location?: string;
    allDay?: boolean;
}

  
  export interface EventFormData {
    name: string;
    date: string;
    startTime: string;
    endTime: string;
    description?: string;
    location: string;
    requiredAttendees: number[];
    optionalAttendees: number[];
    notificationHours: number;
  }


