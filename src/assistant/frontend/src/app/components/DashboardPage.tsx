import { useNavigate } from "react-router";
import {
  Activity, Utensils, Moon, DollarSign, Calendar, CalendarX,
  Clock, BookOpen, Code, Users, MessageCircle, Heart, Target, TrendingUp, TrendingDown, ListChecks, ListTodo, Plus,
} from "lucide-react";
import { EmptyState } from "./EmptyState";
import { useCalendarEvents } from "../../hooks/useCalendar";
import { useChatContext } from "../../contexts/ChatContext";
import { format } from "date-fns";
import { useMemo } from "react";

interface QuickAction {
  label: string;
  description: string;
  prompt: string;
  icon: React.ReactNode;
  bgColor: string;
  color: string;
}

const domainSections: { title: string; actions: QuickAction[] }[] = [
  {
    title: "Wellness",
    actions: [
      { label: "Log Workout", description: "Add exercise session", prompt: "Log a workout session", icon: <Activity className="w-5 h-5" />, bgColor: "bg-green-50", color: "text-green-700" },
      { label: "Log Sleep", description: "Record sleep hours", prompt: "Log my sleep hours from last night", icon: <Moon className="w-5 h-5" />, bgColor: "bg-blue-50", color: "text-blue-700" },
      { label: "Log Meal", description: "Track eating window", prompt: "Log a meal and track my fasting window", icon: <Utensils className="w-5 h-5" />, bgColor: "bg-orange-50", color: "text-orange-700" },
    ],
  },
  {
    title: "Productivity",
    actions: [
      { label: "Log Focus Time", description: "Track deep work", prompt: "Log deep focus work session", icon: <Clock className="w-5 h-5" />, bgColor: "bg-blue-50", color: "text-blue-700" },
      { label: "Log Study", description: "Add study session", prompt: "Log a study session", icon: <BookOpen className="w-5 h-5" />, bgColor: "bg-purple-50", color: "text-purple-700" },
      { label: "Log Coding", description: "Track dev time", prompt: "Log coding session for project", icon: <Code className="w-5 h-5" />, bgColor: "bg-green-50", color: "text-green-700" },
    ],
  },
  {
    title: "Finance",
    actions: [
      { label: "Add Expense", description: "Log spending", prompt: "Add a new expense", icon: <TrendingDown className="w-5 h-5" />, bgColor: "bg-red-50", color: "text-red-700" },
      { label: "Add Income", description: "Log earnings", prompt: "Log income or earnings", icon: <TrendingUp className="w-5 h-5" />, bgColor: "bg-green-50", color: "text-green-700" },
      { label: "View Budget", description: "Check limits", prompt: "Show my current budget status", icon: <DollarSign className="w-5 h-5" />, bgColor: "bg-blue-50", color: "text-blue-700" },
    ],
  },
  {
    title: "Social",
    actions: [
      { label: "Schedule Meeting", description: "Plan a meetup", prompt: "Schedule a meeting with someone", icon: <Calendar className="w-5 h-5" />, bgColor: "bg-blue-50", color: "text-blue-700" },
      { label: "Log Interaction", description: "Record conversation", prompt: "Log a social interaction or conversation", icon: <MessageCircle className="w-5 h-5" />, bgColor: "bg-purple-50", color: "text-purple-700" },
      { label: "Add Contact", description: "New connection", prompt: "Add a new contact to my network", icon: <Heart className="w-5 h-5" />, bgColor: "bg-pink-50", color: "text-pink-700" },
    ],
  },
  {
    title: "Tasks",
    actions: [
      { label: "Add To-Do", description: "Create a new task", prompt: "I need to add a new to-do: ", icon: <ListTodo className="w-5 h-5" />, bgColor: "bg-indigo-50", color: "text-indigo-700" },
      { label: "Break Down Goal", description: "Split into steps", prompt: "Help me break this down into steps: ", icon: <ListChecks className="w-5 h-5" />, bgColor: "bg-violet-50", color: "text-violet-700" },
      { label: "View Tasks", description: "See task board", prompt: "Show me all my current tasks", icon: <Target className="w-5 h-5" />, bgColor: "bg-blue-50", color: "text-blue-700" },
    ],
  },
  {
    title: "Goals",
    actions: [
      { label: "Create Goal", description: "Set a new target", prompt: "Create a new goal", icon: <Target className="w-5 h-5" />, bgColor: "bg-orange-50", color: "text-orange-700" },
      { label: "Update Progress", description: "Log achievements", prompt: "Update progress on my goals", icon: <TrendingUp className="w-5 h-5" />, bgColor: "bg-green-50", color: "text-green-700" },
      { label: "View Goals", description: "Check status", prompt: "Show my active goals and their status", icon: <ListChecks className="w-5 h-5" />, bgColor: "bg-blue-50", color: "text-blue-700" },
    ],
  },
];

export function DashboardPage() {
  const navigate = useNavigate();
  const { prefillChat } = useChatContext();
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
    }));
  }, [calendarData]);

  const handleQuickAction = (prompt: string) => {
    prefillChat(prompt);
    navigate("/");
  };

  return (
    <div className="h-full overflow-auto">
      <div className="max-w-4xl mx-auto p-6 lg:p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl text-gray-900 mb-1">Dashboard</h1>
          <p className="text-sm text-gray-500">{format(today, "EEEE, MMMM d, yyyy")}</p>
        </div>

        {/* Today's Events */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Today's Events</h2>
            <button
              onClick={() => navigate("/calendar")}
              className="text-sm text-gray-500 hover:text-gray-900 flex items-center gap-1.5 transition-colors"
            >
              View calendar
              <Calendar className="w-3.5 h-3.5" />
            </button>
          </div>
          {isLoading ? (
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
                <p className="text-sm text-gray-500">Loading events...</p>
              </div>
            </div>
          ) : todayEvents.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-xl">
              <EmptyState
                icon={CalendarX}
                title="No events today"
                description="Your schedule is clear. Use the chat to add events."
                action={{ label: "Open Chat", onClick: () => navigate("/") }}
              />
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100">
              {todayEvents.map((event, i) => (
                <div key={i} className="px-4 py-3 flex items-center justify-between">
                  <span className="text-sm text-gray-900">{event.title}</span>
                  <span className="text-xs text-gray-500">{event.time}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions by Domain */}
        {domainSections.map((section) => (
          <div key={section.title} className="mb-8">
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">{section.title}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {section.actions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleQuickAction(action.prompt)}
                  className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-sm transition-all text-left group"
                >
                  <div className={`w-9 h-9 rounded-lg ${action.bgColor} ${action.color} flex items-center justify-center flex-shrink-0`}>
                    {action.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900">{action.label}</div>
                    <div className="text-xs text-gray-500">{action.description}</div>
                  </div>
                  <Plus className="w-3.5 h-3.5 text-gray-300 group-hover:text-gray-500 transition-colors flex-shrink-0" />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
