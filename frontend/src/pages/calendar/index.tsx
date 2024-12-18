import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';
import styles from '@/styles/Calendar.module.css';
import { eventService, CalendarEvent } from '@/services/eventService';
import EventModal from '@/components/EventModal';
import { 
  EventClickArg, 
  DateSelectArg, 
  EventChangeArg,
  EventInput 
} from '@fullcalendar/core';

// Import plugins directly
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

const FullCalendar = dynamic(() => 
  import('@fullcalendar/react').then(mod => mod.default), 
  { 
    ssr: false,
    loading: () => <p>Loading calendar...</p>
  }
);

export default function CalendarPage() {
  const router = useRouter();
  const [events, setEvents] = useState<EventInput[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Partial<CalendarEvent> | undefined>();
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');

  useEffect(() => {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    if (!isLoggedIn) {
      router.push('/login');
    }
  }, [router]);

  const fetchEvents = useCallback(async () => {
    try {
      setIsLoading(true);
      const fetchedEvents = await eventService.getAllEvents();
      setEvents(fetchedEvents);
    } catch (error) {
      console.error('Error fetching events:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch events');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleLogout = async () => {
    try {
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('user');
      await router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Loading calendar...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button 
            onClick={fetchEvents}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const handleDateSelect = (selectInfo: DateSelectArg) => {
    setModalMode('create');
    const localStart = new Date(selectInfo.start.getTime() - selectInfo.start.getTimezoneOffset() * 60000);
    const localEnd = new Date(selectInfo.end.getTime() - selectInfo.end.getTimezoneOffset() * 60000);
    
    setSelectedEvent({
      start: localStart,
      end: localEnd,
      allDay: selectInfo.allDay
    });
    setModalOpen(true);
  };

  const handleEventClick = (clickInfo: EventClickArg) => {
    setModalMode('edit');
    const eventData: CalendarEvent = {
      id: clickInfo.event.id,
      title: clickInfo.event.title,
      start: clickInfo.event.start || new Date(),
      end: clickInfo.event.end || new Date(),
      description: clickInfo.event.extendedProps.description,
      allDay: clickInfo.event.allDay,
      backgroundColor: clickInfo.event.backgroundColor
    };
    setSelectedEvent(eventData);
    setModalOpen(true);
  };

  const handleEventChange = async (changeInfo: EventChangeArg) => {
    try {
      const updatedEvent: CalendarEvent = {
        id: changeInfo.event.id,
        title: changeInfo.event.title,
        start: changeInfo.event.start || new Date(),
        end: changeInfo.event.end || new Date(),
        description: changeInfo.event.extendedProps.description,
        allDay: changeInfo.event.allDay,
        backgroundColor: changeInfo.event.backgroundColor
      };
      await eventService.updateEvent(updatedEvent);
      await fetchEvents();
    } catch (error) {
      console.error('Error updating event:', error);
      changeInfo.revert();
    }
  };

  const handleSaveEvent = async (eventData: Partial<CalendarEvent>) => {
    try {
      if (modalMode === 'create') {
        await eventService.createEvent(eventData);
      } else {
        await eventService.updateEvent(eventData as CalendarEvent);
      }
      await fetchEvents();
      setModalOpen(false);
    } catch (error) {
      console.error('Error saving event:', error);
      // Handle error (show toast notification, etc.)
    }
  };

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div>
            <h1 className={styles.welcomeText}>
              Calendar
            </h1>
            <p className={styles.subText}>
              Manage your events and schedule
            </p>
          </div>
          <div className={styles.headerButtons}>
            <button
              onClick={() => {
                setModalMode('create');
                setSelectedEvent(undefined);
                setModalOpen(true);
              }}
              className={styles.addButton}
            >
              Add Event
            </button>
            <button
              onClick={handleLogout}
              className={styles.logoutButton}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className={styles.calendarContainer}>
        <div className={styles.calendarWrapper}>
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="timeGridWeek"
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek,timeGridDay'
            }}
            editable={true}
            selectable={true}
            selectMirror={true}
            dayMaxEvents={true}
            weekends={true}
            events={events}
            select={handleDateSelect}
            eventClick={handleEventClick}
            eventChange={handleEventChange}
            height="auto"
            aspectRatio={1.8}
          />
        </div>
      </main>

      <EventModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedEvent(undefined);
        }}
        onSave={handleSaveEvent}
        event={selectedEvent}
        mode={modalMode}
      />
    </div>
  );
} 