import { FC, useState, useEffect } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { Event } from '@/types/event'

interface CalendarProps {
    initialEvents?: Event[];
    onEventClick?: (event: Event) => void;
    onDateSelect?: (start: Date, end: Date) => void;
}

// Make a calendar component that displays the events in the calendar
export const Calendar: FC<CalendarProps> = ({
    initialEvents = [],
    onEventClick,
    onDateSelect,
}) => {
    const [events, setEvents] = useState<Event[]>(initialEvents);

    const handleEventClick = (clickInfo: any) => {
        if (onEventClick) {
            onEventClick(clickInfo.event);
        }
    };

    const handleDateSelect = (selectInfo: any) => {
        if (onDateSelect) {
            onDateSelect(selectInfo.start, selectInfo.end);
        }
    };

    return (
        <div className="h-screen p-4">
        <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="timeGridWeek"
            headerToolbar={{
                left: "prev,next today",
                center: "title",
                right: "dayGridMonth,timeGridWeek,timeGridDay"
            }}
            editable={true}
            selectable={true}
            selectMirror={true}
            dayMaxEvents={true}
            weekends={true}
            events={events}
            select={handleDateSelect}
            eventClick={handleEventClick}
        />
        </div>
    );
};