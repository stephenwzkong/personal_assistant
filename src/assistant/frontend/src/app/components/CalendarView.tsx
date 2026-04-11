import { useState, useCallback, useMemo } from "react";
import { Calendar as BigCalendar, dateFnsLocalizer, View } from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import { enUS } from "date-fns/locale";
import { ChevronLeft, ChevronRight, Home as HomeIcon } from "lucide-react";
import { useCalendarEvents } from "../../hooks/useCalendar";
import "react-big-calendar/lib/css/react-big-calendar.css";

const locales = {
  "en-US": enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface CalendarEvent {
  id: number;
  title: string;
  start: Date;
  end: Date;
  description?: string;
}

export function CalendarView() {
  const [view, setView] = useState<View>("week");
  const [date, setDate] = useState(new Date());

  // Compute date range for current view
  const { startDate, endDate } = useMemo(() => {
    const d = new Date(date);
    let start: Date;
    let end: Date;
    if (view === "month") {
      start = new Date(d.getFullYear(), d.getMonth(), 1);
      end = new Date(d.getFullYear(), d.getMonth() + 1, 0);
    } else if (view === "week") {
      const day = d.getDay();
      const diff = d.getDate() - day + (day === 0 ? -6 : 1);
      start = new Date(d.getFullYear(), d.getMonth(), diff);
      end = new Date(start);
      end.setDate(start.getDate() + 6);
    } else {
      start = new Date(d);
      end = new Date(d);
    }
    return {
      startDate: start.toISOString().slice(0, 10),
      endDate: end.toISOString().slice(0, 10),
    };
  }, [date, view]);

  const { data } = useCalendarEvents(startDate, endDate);

  const events: CalendarEvent[] = useMemo(() => {
    if (!data?.events) return [];
    return data.events.map((evt: { event_id?: string; title?: string; event_title?: string; start_date?: string; end_date?: string; start_time?: string; end_time?: string; description?: string }, i: number) => {
      const startStr = evt.start_date || "";
      const endStr = evt.end_date || startStr;
      const startTime = evt.start_time || "00:00";
      const endTime = evt.end_time || "23:59";
      return {
        id: i,
        title: evt.title || evt.event_title || "Event",
        start: new Date(`${startStr}T${startTime}`),
        end: new Date(`${endStr}T${endTime}`),
        description: evt.description,
      };
    });
  }, [data]);

  const handleSelectSlot = useCallback(
    ({ start, end }: { start: Date; end: Date }) => {
      const title = window.prompt("Enter event title:");
      if (title) {
        // For now just show — real creation goes through chat
        alert(`To create "${title}", use the chat: "Schedule ${title} on ${format(start, "MMM d")} at ${format(start, "h:mm a")}"`);
      }
    },
    []
  );

  const handleSelectEvent = useCallback((event: CalendarEvent) => {
    alert(`Event: ${event.title}\n${event.description || ""}`);
  }, []);

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Calendar Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-4 text-sm text-gray-500">
          <HomeIcon className="w-4 h-4" />
          <span>/</span>
          <span className="text-gray-900">Calendar</span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl text-gray-900">
              {format(date, "MMMM yyyy")}
            </h2>
            <div className="flex items-center gap-1">
              <button
                onClick={() => {
                  const newDate = new Date(date);
                  if (view === "month") {
                    newDate.setMonth(date.getMonth() - 1);
                  } else {
                    newDate.setDate(date.getDate() - 7);
                  }
                  setDate(newDate);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-4 h-4 text-gray-600" />
              </button>
              <button
                onClick={() => setDate(new Date())}
                className="px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Today
              </button>
              <button
                onClick={() => {
                  const newDate = new Date(date);
                  if (view === "month") {
                    newDate.setMonth(date.getMonth() + 1);
                  } else {
                    newDate.setDate(date.getDate() + 7);
                  }
                  setDate(newDate);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronRight className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setView("day")}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  view === "day"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Day
              </button>
              <button
                onClick={() => setView("week")}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  view === "week"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Week
              </button>
              <button
                onClick={() => setView("month")}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  view === "month"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Month
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Calendar Content */}
      <div className="flex-1 p-6 overflow-auto">
        <style>{`
          .rbc-calendar {
            font-family: inherit;
            height: 100%;
          }
          .rbc-header {
            padding: 12px 4px;
            font-weight: 500;
            color: rgb(75, 85, 99);
            font-size: 0.875rem;
            border-bottom: 1px solid rgb(229, 231, 235);
          }
          .rbc-today {
            background-color: rgb(249, 250, 251);
          }
          .rbc-event {
            background-color: rgb(31, 41, 55);
            border-radius: 6px;
            border: none;
            padding: 6px 10px;
            font-size: 0.875rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: all 0.2s;
          }
          .rbc-event:hover {
            background-color: rgb(17, 24, 39);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
          }
          .rbc-selected {
            background-color: rgb(17, 24, 39);
          }
          .rbc-time-slot {
            min-height: 40px;
          }
          .rbc-timeslot-group {
            min-height: 80px;
            border-left: 1px solid rgb(229, 231, 235);
          }
          .rbc-day-slot .rbc-time-slot {
            border-top: 1px solid rgb(243, 244, 246);
          }
          .rbc-current-time-indicator {
            background-color: rgb(239, 68, 68);
          }
          .rbc-off-range-bg {
            background-color: rgb(249, 250, 251);
          }
          .rbc-toolbar {
            display: none;
          }
        `}</style>
        <BigCalendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          view={view}
          onView={setView}
          date={date}
          onNavigate={setDate}
          onSelectSlot={handleSelectSlot}
          onSelectEvent={handleSelectEvent}
          selectable
          popup
          className="bg-white rounded-lg border border-gray-200"
        />
      </div>
    </div>
  );
}
