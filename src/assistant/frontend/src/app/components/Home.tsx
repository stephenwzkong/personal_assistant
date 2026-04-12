import { useNavigate } from "react-router";
import { Activity, Utensils, Moon, DollarSign, Calendar, Home as HomeIcon, CalendarX } from "lucide-react";
import { EmptyState } from "./EmptyState";
import { useCalendarEvents } from "../../hooks/useCalendar";
import { format } from "date-fns";
import { useMemo } from "react";

interface DomainCard {
  id: string;
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

export function Home() {
  const navigate = useNavigate();
  const today = new Date();
  const todayStr = format(today, "yyyy-MM-dd");

  const { data: calendarData, isLoading } = useCalendarEvents(todayStr, todayStr);

  const todayEvents = useMemo(() => {
    if (!calendarData?.events) return [];
    return calendarData.events.map((evt) => ({
      time: evt.start_datetime
        ? format(new Date(evt.start_datetime), "h:mm a")
        : evt.time || "",
      title: evt.title || evt.event_type || "Event",
      type: evt.event_type || "general",
    }));
  }, [calendarData]);

  const domainCards: DomainCard[] = [
    {
      id: "wellness",
      title: "Fitness",
      value: "Track",
      subtitle: "Log workouts & progress",
      icon: <Activity className="w-5 h-5" />,
      color: "text-green-700",
      bgColor: "bg-green-50",
    },
    {
      id: "wellness",
      title: "Meals",
      value: "Track",
      subtitle: "Log meals & fasting",
      icon: <Utensils className="w-5 h-5" />,
      color: "text-orange-700",
      bgColor: "bg-orange-50",
    },
    {
      id: "wellness",
      title: "Sleep",
      value: "Track",
      subtitle: "Monitor sleep quality",
      icon: <Moon className="w-5 h-5" />,
      color: "text-blue-700",
      bgColor: "bg-blue-50",
    },
    {
      id: "finance",
      title: "Finance",
      value: "Track",
      subtitle: "Log spending & income",
      icon: <DollarSign className="w-5 h-5" />,
      color: "text-purple-700",
      bgColor: "bg-purple-50",
    },
  ];

  const handleCardClick = (domainId: string) => {
    navigate(`/domains?tab=${domainId}`);
  };

  return (
    <div className="h-full overflow-auto">
      <div className="max-w-6xl mx-auto p-6 lg:p-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-6 text-sm text-gray-500">
          <HomeIcon className="w-4 h-4" />
          <span>/</span>
          <span className="text-gray-900">Dashboard</span>
        </div>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl text-gray-900 mb-2">Today at a Glance</h1>
          <p className="text-gray-600">
            {format(today, "EEEE, MMMM d, yyyy")}
          </p>
        </div>

        {/* Domain Cards Grid */}
        <div className="mb-8">
          <h2 className="text-lg text-gray-900 mb-6">Quick Access</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {domainCards.map((card) => (
              <button
                key={card.title}
                onClick={() => handleCardClick(card.id)}
                title={`Click to view ${card.title} details`}
                className="group p-6 bg-white border border-gray-200 rounded-2xl hover:border-gray-300 hover:shadow-lg transition-all text-left cursor-pointer"
              >
                <div className={`w-10 h-10 rounded-xl ${card.bgColor} ${card.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  {card.icon}
                </div>
                <div className="text-sm font-medium text-gray-900">{card.title}</div>
                <div className="text-xs text-gray-500 mt-1">{card.subtitle}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Today's Events */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl text-gray-900">Today's Events</h2>
            <button
              onClick={() => navigate("/calendar")}
              className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            >
              View calendar
              <Calendar className="w-4 h-4" />
            </button>
          </div>
          {isLoading ? (
            <div className="bg-white border border-gray-200 rounded-2xl p-8">
              <div className="flex flex-col items-center gap-3">
                <div className="w-6 h-6 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
                <p className="text-sm text-gray-500">Loading events...</p>
              </div>
            </div>
          ) : todayEvents.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-2xl">
              <EmptyState
                icon={CalendarX}
                title="No events today"
                description="You have a clear schedule today. Use the assistant to schedule new activities."
                action={{
                  label: "View Calendar",
                  onClick: () => navigate("/calendar")
                }}
              />
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-2xl divide-y divide-gray-100">
              {todayEvents.map((event, index) => (
                <div
                  key={index}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{event.title}</div>
                      <div className="text-sm text-gray-500 mt-1">{event.time}</div>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-gray-900"></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
