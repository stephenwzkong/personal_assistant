import { Activity, Moon, Utensils, Plus, TrendingUp } from "lucide-react";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const sleepData = [
  { day: "Mon", hours: 7.5 },
  { day: "Tue", hours: 6.8 },
  { day: "Wed", hours: 7.2 },
  { day: "Thu", hours: 8.0 },
  { day: "Fri", hours: 7.0 },
  { day: "Sat", hours: 8.5 },
  { day: "Sun", hours: 7.2 },
];

const workoutData = [
  { day: "Mon", minutes: 45 },
  { day: "Tue", minutes: 0 },
  { day: "Wed", minutes: 60 },
  { day: "Thu", minutes: 30 },
  { day: "Fri", minutes: 45 },
  { day: "Sat", minutes: 0 },
  { day: "Sun", minutes: 90 },
];

interface RecentEntry {
  date: string;
  type: string;
  value: string;
  note?: string;
}

const recentEntries: RecentEntry[] = [
  { date: "Today, 7:30 AM", type: "Workout", value: "45 min cardio", note: "Morning run" },
  { date: "Today, 11:00 PM", type: "Sleep", value: "7.2 hours", note: "Good quality" },
  { date: "Yesterday, 12:00 PM", type: "Meal", value: "Breaking fast", note: "16h fast completed" },
  { date: "Yesterday, 6:00 PM", type: "Workout", value: "60 min strength", note: "Upper body" },
  { date: "Mar 14", type: "Sleep", value: "8.0 hours" },
];

interface WellnessTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function WellnessTab({ onQuickAction }: WellnessTabProps) {
  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-4">
        <button
          onClick={() => onQuickAction?.("Log a workout session")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-green-50 text-green-700 flex items-center justify-center">
            <Activity className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Workout</div>
            <div className="text-xs text-gray-500">Add exercise session</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Log my sleep hours from last night")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <Moon className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Sleep</div>
            <div className="text-xs text-gray-500">Record sleep hours</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Log a meal and track my fasting window")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-orange-50 text-orange-700 flex items-center justify-center">
            <Utensils className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Meal</div>
            <div className="text-xs text-gray-500">Track eating window</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="p-6 bg-white border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-medium text-gray-900">Sleep Trend</h3>
              <p className="text-sm text-gray-500 mt-1">Last 7 days</p>
            </div>
            <div className="flex items-center gap-1 text-green-600">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-medium">+8%</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={sleepData}>
              <defs>
                <linearGradient id="sleepGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="day" stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <Tooltip />
              <Area type="monotone" dataKey="hours" stroke="#3b82f6" fill="url(#sleepGradient)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="p-6 bg-white border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-medium text-gray-900">Workout Minutes</h3>
              <p className="text-sm text-gray-500 mt-1">Last 7 days</p>
            </div>
            <div className="text-sm font-medium text-gray-900">270 min total</div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={workoutData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="day" stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <Tooltip />
              <Bar dataKey="minutes" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-gradient-to-br from-green-50 to-white border border-green-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">3</div>
          <div className="text-sm text-gray-600 mt-1">Day streak</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-blue-50 to-white border border-blue-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">7.3h</div>
          <div className="text-sm text-gray-600 mt-1">Avg sleep</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-orange-50 to-white border border-orange-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">16:8</div>
          <div className="text-sm text-gray-600 mt-1">Fasting ratio</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">5</div>
          <div className="text-sm text-gray-600 mt-1">Workouts/week</div>
        </div>
      </div>

      {/* Recent Entries */}
      <div className="p-6 bg-white border border-gray-200 rounded-xl">
        <h3 className="font-medium text-gray-900 mb-4">Recent Entries</h3>
        <div className="space-y-3">
          {recentEntries.map((entry, index) => (
            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-900">{entry.type}</span>
                  <span className="text-sm text-gray-600">{entry.value}</span>
                </div>
                {entry.note && (
                  <div className="text-xs text-gray-500 mt-1">{entry.note}</div>
                )}
              </div>
              <div className="text-xs text-gray-400">{entry.date}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}