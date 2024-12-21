'use client';

import { useEffect, useState, useCallback } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { useRouter } from 'next/navigation';
import styles from '@/styles/calendar.module.css';
import { FaSun, FaMoon } from 'react-icons/fa';
import { ApiService } from '@/services/api';
import type { EventSourceInput, DateSelectArg, EventClickArg, DatesSetArg } from '@fullcalendar/core';
import EventFormModal from '@/components/EventFormModal';

interface DateClickArg {
  date: Date;
  dateStr: string;
  allDay: boolean;
  dayEl: HTMLElement;
  jsEvent: MouseEvent;
  view: {
    type: string;
    title: string;
    currentStart: Date;
    currentEnd: Date;
  };
}

export default function CalendarPage() {
  const [username, setUsername] = useState<string>('');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [events, setEvents] = useState<EventSourceInput>([]);
  const [showEventModal, setShowEventModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const router = useRouter();

  const fetchEvents = useCallback(async (start: Date, end: Date) => {
    try {
      const startStr = start.toISOString().split('T')[0];
      const endStr = end.toISOString().split('T')[0];
      const fetchedEvents = await ApiService.getEvents(startStr, endStr);
      setEvents(fetchedEvents);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  }, []);

  // Handle date range changes
  const handleDatesSet = useCallback((arg: DatesSetArg) => {
    fetchEvents(arg.start, arg.end);
  }, [fetchEvents]);

  // Handle event click
  const handleEventClick = useCallback((clickInfo: EventClickArg) => {
    // You can implement event editing here
    console.log('Event clicked:', clickInfo.event);
  }, []);

  // Handle date select for new event
  const handleDateSelect = useCallback((selectInfo: DateSelectArg) => {
    // You can implement new event creation here
    console.log('Date selected:', selectInfo);
  }, []);

  // Handle date click
  const handleDateClick = (arg: DateClickArg) => {
    setSelectedDate(arg.date);
    setSelectedTime(arg.date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    setShowEventModal(true);
  };

  // Handle date selection (drag)
  const handleSelect = useCallback((selectInfo: DateSelectArg) => {
    setSelectedDate(selectInfo.start);
    setSelectedTime(selectInfo.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    setShowEventModal(true);
  }, []);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      router.push('/login');
      return;
    }
    const user = JSON.parse(userData);
    setUsername(user.username);

    const savedTheme = localStorage.getItem('theme');
    setIsDarkMode(savedTheme === 'dark');

    // Initial events fetch
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), 1); // Start of current month
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0); // End of current month
    fetchEvents(start, end);
  }, [router, fetchEvents]);

  return (
    <div className={`${styles.pageContainer} ${isDarkMode ? styles.darkMode : styles.lightMode}`}>
      <nav className={styles.navbar}>
        <h1 className={styles.welcomeHeader}>{username}&apos;s Schedule</h1>
        <div className={styles.navButtons}>
          <button 
            className={styles.themeToggle} 
            onClick={() => {
              const newTheme = !isDarkMode;
              setIsDarkMode(newTheme);
              localStorage.setItem('theme', newTheme ? 'dark' : 'light');
            }}
            aria-label="Toggle theme"
          >
            {isDarkMode ? <FaSun /> : <FaMoon />}
          </button>
          <button className={styles.logoutButton} onClick={() => router.push('/login')}>
            Logout
          </button>
        </div>
      </nav>
      
      <div className={styles.calendarContainer}>
        <div className={styles.calendarHeader}>
          <button 
            className={styles.addEventButton}
            onClick={() => {
              setSelectedDate(new Date());
              setSelectedTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
              setShowEventModal(true);
            }}
          >
            Add Event
          </button>
        </div>
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
            height="auto"
            events={events}
            slotMinTime="06:00:00"
            slotMaxTime="22:00:00"
            datesSet={handleDatesSet}
            eventClick={handleEventClick}
            select={handleDateSelect}
            eventTimeFormat={{
              hour: '2-digit',
              minute: '2-digit',
              meridiem: 'short'
            }}
            dateClick={handleDateClick}
            select={handleSelect}
          />
        </div>
      </div>

      <EventFormModal
        isOpen={showEventModal}
        onClose={() => setShowEventModal(false)}
        selectedDate={selectedDate || undefined}
        selectedTime={selectedTime || undefined}
      />
    </div>
  );
}