import { Calendar } from '@/components/Calendar/Calendar';

export default function Home() {
  return (
    <div className="container mx-auto">
      <Calendar 
        initialEvents={[
          {
            id: "1",
            title: "Team Meeting",
            start: new Date().toISOString(), // Today
            end: new Date(new Date().setHours(new Date().getHours() + 1)).toISOString(), // 1 hour later
          }
        ]}
      />
    </div>
  );
}