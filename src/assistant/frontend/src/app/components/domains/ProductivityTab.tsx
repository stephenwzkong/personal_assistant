import { Clock, BookOpen, Code, Plus, TrendingUp } from "lucide-react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const focusTimeData = [
  { day: "Mon", hours: 6.5 },
  { day: "Tue", hours: 7.2 },
  { day: "Wed", hours: 5.8 },
  { day: "Thu", hours: 8.0 },
  { day: "Fri", hours: 6.0 },
  { day: "Sat", hours: 4.5 },
  { day: "Sun", hours: 5.0 },
];

const tasksData = [
  { day: "Mon", completed: 8, total: 10 },
  { day: "Tue", completed: 12, total: 14 },
  { day: "Wed", completed: 9, total: 12 },
  { day: "Thu", completed: 11, total: 11 },
  { day: "Fri", completed: 7, total: 9 },
  { day: "Sat", completed: 5, total: 6 },
  { day: "Sun", completed: 4, total: 5 },
];

interface RecentActivity {
  date: string;
  activity: string;
  duration: string;
  type: string;
}

const recentActivities: RecentActivity[] = [
  { date: "Today, 9:00 AM", activity: "CS Lecture", duration: "2 hours", type: "Study" },
  { date: "Today, 2:00 PM", activity: "Project work", duration: "3 hours", type: "Coding" },
  { date: "Yesterday, 10:00 AM", activity: "Deep work session", duration: "4 hours", type: "Focus" },
  { date: "Yesterday, 3:00 PM", activity: "Team meeting", duration: "1 hour", type: "Meeting" },
  { date: "Mar 14", activity: "Study session", duration: "2.5 hours", type: "Study" },
];

interface ProductivityTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function ProductivityTab({ onQuickAction }: ProductivityTabProps) {
  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-4">
        <button
          onClick={() => onQuickAction?.("Log deep focus work session")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Focus Time</div>
            <div className="text-xs text-gray-500">Track deep work</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Log a study session")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
            <BookOpen className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Study</div>
            <div className="text-xs text-gray-500">Add study session</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Log coding session for project")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-green-50 text-green-700 flex items-center justify-center">
            <Code className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Coding</div>
            <div className="text-xs text-gray-500">Track dev time</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>
      </div>

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="p-6 bg-white border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-medium text-gray-900">Focus Time</h3>
              <p className="text-sm text-gray-500 mt-1">Hours per day</p>
            </div>
            <div className="flex items-center gap-1 text-green-600">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-medium">+12%</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={focusTimeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="day" stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <Tooltip />
              <Line type="monotone" dataKey="hours" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="p-6 bg-white border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-medium text-gray-900">Tasks Completed</h3>
              <p className="text-sm text-gray-500 mt-1">This week</p>
            </div>
            <div className="text-sm font-medium text-gray-900">56/57 (98%)</div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={tasksData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="day" stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <Tooltip />
              <Bar dataKey="completed" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-gradient-to-br from-blue-50 to-white border border-blue-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">48h</div>
          <div className="text-sm text-gray-600 mt-1">Weekly focus</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">98%</div>
          <div className="text-sm text-gray-600 mt-1">Task completion</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-green-50 to-white border border-green-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">12</div>
          <div className="text-sm text-gray-600 mt-1">Study hours</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-orange-50 to-white border border-orange-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">24</div>
          <div className="text-sm text-gray-600 mt-1">Coding hours</div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="p-6 bg-white border border-gray-200 rounded-xl">
        <h3 className="font-medium text-gray-900 mb-4">Recent Activities</h3>
        <div className="space-y-3">
          {recentActivities.map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-900">{activity.activity}</span>
                  <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{activity.type}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">{activity.duration}</div>
              </div>
              <div className="text-xs text-gray-400">{activity.date}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}