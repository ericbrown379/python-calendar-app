import React, { useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
// import { useSocket } from "hooks/useSocket";

// Define the type for the Event
interface Event {
    id: string;
    title: string;
    start: string; // ISO date format
    end: string;
}

const WeekView = () => {
    // Explicitly define the type of the state as an array of Event
    const [events, setEvents] = useState<Event[]>([]);

    // WebSocket for real-time updates
    // useSocket("update_calendar", (newEvent: Event) => {
    //     setEvents((prevEvents) => [...prevEvents, newEvent]);
    // });

    const handleDateClick = (info: { dateStr: string }) => {
        alert(`Date clicked: ${info.dateStr}`);
    };

    return (
        <FullCalendar
            plugins={[dayGridPlugin, interactionPlugin]}
            initialView="dayGridWeek"
            events={events}
            dateClick={handleDateClick}
        />
    );
};

export default WeekView;