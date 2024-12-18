import { useEffect, useState } from 'react'
import styles from '@/styles/auth.module.css'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const HOURS = Array.from({ length: 24 }, (_, i) => 
  i < 12 ? `${i || 12}AM` : `${i === 12 ? 12 : i - 12}PM`
)

const DEMO_EVENTS = [
  { title: 'Team Meeting', start: 9, duration: 1, day: 1, color: '#0066ff' },
  { title: 'Project Review', start: 14, duration: 2, day: 3, color: '#00cc66' },
  { title: 'Client Call', start: 11, duration: 1, day: 2, color: '#ff3366' },
  { title: 'Lunch Break', start: 12, duration: 1, day: 4, color: '#ffcc00' }
]

export function CalendarBackground() {
  const [events, setEvents] = useState(DEMO_EVENTS)

  useEffect(() => {
    const interval = setInterval(() => {
      const newEvents = [...events]
      if (Math.random() > 0.7) {
        const start = Math.floor(Math.random() * 12 + 8)
        newEvents.push({
          title: `Event ${Math.floor(Math.random() * 100)}`,
          start,
          duration: Math.floor(Math.random() * 2) + 1,
          day: Math.floor(Math.random() * 7),
          color: ['#0066ff', '#00cc66', '#ff3366', '#ffcc00'][Math.floor(Math.random() * 4)]
        })
      }
      if (newEvents.length > 6) {
        newEvents.shift()
      }
      setEvents(newEvents)
    }, 3000)

    return () => clearInterval(interval)
  }, [events])

  return (
    <div className={styles.calendarBackground}>
      <div className={styles.calendarPreview}>
        <div className={styles.calendarHeader}>
          {DAYS.map(day => (
            <div key={day} className={styles.dayHeader}>{day}</div>
          ))}
        </div>
        <div className={styles.calendarGrid}>
          {DAYS.map((_, dayIndex) => (
            <div key={dayIndex} className={styles.calendarColumn}>
              {HOURS.map((hour, hourIndex) => (
                <div key={hourIndex} className={styles.calendarCell}>
                  {hourIndex === 0 && <div className={styles.hourMarker}>{hour}</div>}
                </div>
              ))}
              {events
                .filter(event => event.day === dayIndex)
                .map((event, i) => (
                  <div
                    key={i}
                    className={styles.calendarEvent}
                    style={{
                      top: `${(event.start * 100) / 24}%`,
                      height: `${(event.duration * 100) / 24}%`,
                      backgroundColor: event.color
                    }}
                  >
                    {event.title}
                  </div>
                ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 