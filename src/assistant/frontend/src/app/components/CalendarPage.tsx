import { CalendarView } from "./CalendarView";
import { FloatingChat } from "./FloatingChat";

export function CalendarPage() {
  return (
    <div className="h-full bg-white relative">
      <CalendarView />
      <FloatingChat />
    </div>
  );
}