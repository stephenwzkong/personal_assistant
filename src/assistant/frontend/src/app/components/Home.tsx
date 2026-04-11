import { useNavigate } from "react-router";
import { Activity, Utensils, Moon, DollarSign, Calendar, TrendingUp, Home as HomeIcon, CalendarX, MessageCircle } from "lucide-react";
import { ChatInterface } from "./ChatInterface";
import { EmptyState } from "./EmptyState";
import { useState } from "react";

interface DomainCard {
  id: string;
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

interface TodayEvent {
  time: string;
  title: string;
  type: string;
}

export function Home() {
  const navigate = useNavigate();
  const [showMobileChat, setShowMobileChat] = useState(false);

  const domainCards: DomainCard[] = [
    {
      id: "wellness",
      title: "Fitness",
      value: "3 days",
      subtitle: "Workout streak",
      icon: <Activity className="w-5 h-5" />,
      color: "text-green-700",
      bgColor: "bg-green-50",
    },
    {
      id: "wellness",
      title: "Meals",
      value: "8h fast",
      subtitle: "Intermittent fasting",
      icon: <Utensils className="w-5 h-5" />,
      color: "text-orange-700",
      bgColor: "bg-orange-50",
    },
    {
      id: "wellness",
      title: "Sleep",
      value: "7.2h",
      subtitle: "Last night",
      icon: <Moon className="w-5 h-5" />,
      color: "text-blue-700",
      bgColor: "bg-blue-50",
    },
    {
      id: "finance",
      title: "Finance",
      value: "$240",
      subtitle: "Week spending",
      icon: <DollarSign className="w-5 h-5" />,
      color: "text-purple-700",
      bgColor: "bg-purple-50",
    },
  ];

  const todayEvents: TodayEvent[] = [
    { time: "9:00 AM", title: "CS Lecture", type: "productivity" },
    { time: "12:00 PM", title: "Meal window opens", type: "wellness" },
    { time: "3:00 PM", title: "Team Meeting", type: "social" },
    { time: "6:00 PM", title: "Gym session", type: "wellness" },
  ];

  const handleCardClick = (domainId: string) => {
    navigate(`/domains?tab=${domainId}`);
  };

  return (
    <div className="h-full bg-white relative">
      <div className="h-full grid grid-cols-1 lg:grid-cols-[450px_1fr] xl:grid-cols-[500px_1fr]">
        {/* AI Chat - Left Side (Desktop only) */}
        <div className="hidden lg:block border-r border-gray-200">
          <ChatInterface />
        </div>

        {/* Mobile Chat Button */}
        <button
          onClick={() => setShowMobileChat(!showMobileChat)}
          className="lg:hidden fixed bottom-6 right-6 w-14 h-14 bg-gray-900 text-white rounded-full shadow-lg hover:bg-gray-800 transition-all flex items-center justify-center z-50"
        >
          <MessageCircle className="w-6 h-6" />
        </button>

        {/* Mobile Chat Overlay */}
        {showMobileChat && (
          <div className="lg:hidden fixed inset-0 bg-white z-50">
            <div className="h-full flex flex-col">
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
                <h2 className="text-lg text-gray-900">AI Assistant</h2>
                <button
                  onClick={() => setShowMobileChat(false)}
                  className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900"
                >
                  Close
                </button>
              </div>
              <div className="flex-1">
                <ChatInterface />
              </div>
            </div>
          </div>
        )}

        {/* Main Content - Right Side */}
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
              <p className="text-gray-600">Monday, March 30, 2026</p>
            </div>

              {/* Domain Cards Grid */}
              <div className="mb-8">
                <h2 className="text-lg text-gray-900 mb-6">Your Metrics</h2>
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
                      <div className="text-2xl font-medium text-gray-900 mb-1">{card.value}</div>
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
                {todayEvents.length === 0 ? (
                  <div className="bg-white border border-gray-200 rounded-2xl">
                    <EmptyState
                      icon={CalendarX}
                      title="No events today"
                      description="You have a clear schedule today. Use this time to focus on your goals or schedule new activities."
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
                      className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
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

              {/* Quick Stats */}
              <div className="mt-8 p-6 bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-2xl">
                <div className="flex items-center gap-2 mb-6">
                  <TrendingUp className="w-5 h-5 text-gray-700" />
                  <h2 className="text-lg text-gray-900">This Week</h2>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-2xl font-medium text-gray-900">5</div>
                    <div className="text-xs text-gray-500">Workouts</div>
                  </div>
                  <div>
                    <div className="text-2xl font-medium text-gray-900">48h</div>
                    <div className="text-xs text-gray-500">Focus time</div>
                  </div>
                  <div>
                    <div className="text-2xl font-medium text-gray-900">92%</div>
                    <div className="text-xs text-gray-500">Goal progress</div>
                  </div>
                </div>
              </div>
          </div>
        </div>
      </div>
    </div>
  );
}