import { Users, MessageCircle, Calendar, Heart, Plus } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const interactionData = [
  { day: "Mon", meetings: 3, messages: 45 },
  { day: "Tue", meetings: 2, messages: 38 },
  { day: "Wed", meetings: 4, messages: 52 },
  { day: "Thu", meetings: 1, messages: 30 },
  { day: "Fri", meetings: 3, messages: 48 },
  { day: "Sat", meetings: 2, messages: 25 },
  { day: "Sun", meetings: 1, messages: 18 },
];

interface SocialActivity {
  date: string;
  activity: string;
  people: string;
  type: string;
}

const recentActivities: SocialActivity[] = [
  { date: "Today, 3:00 PM", activity: "Team Meeting", people: "Work team", type: "Meeting" },
  { date: "Today, 12:30 PM", activity: "Lunch with Sarah", people: "Sarah Johnson", type: "Social" },
  { date: "Yesterday, 6:00 PM", activity: "Study group", people: "CS classmates", type: "Study" },
  { date: "Yesterday, 4:00 PM", activity: "Coffee chat", people: "Alex Chen", type: "Social" },
  { date: "Mar 14", activity: "Family dinner", people: "Family", type: "Family" },
];

interface SocialTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function SocialTab({ onQuickAction }: SocialTabProps) {
  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-4">
        <button
          onClick={() => onQuickAction?.("Schedule a meeting with someone")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <Calendar className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Schedule Meeting</div>
            <div className="text-xs text-gray-500">Plan a meetup</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Log a social interaction or conversation")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
            <MessageCircle className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Log Interaction</div>
            <div className="text-xs text-gray-500">Record conversation</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Add a new contact to my network")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-pink-50 text-pink-700 flex items-center justify-center">
            <Heart className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Add Contact</div>
            <div className="text-xs text-gray-500">New connection</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>
      </div>

      {/* Chart */}
      <div className="p-6 bg-white border border-gray-200 rounded-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-medium text-gray-900">Social Interactions</h3>
            <p className="text-sm text-gray-500 mt-1">Meetings and messages this week</p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={interactionData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="day" stroke="#9ca3af" style={{ fontSize: '12px' }} />
            <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
            <Tooltip />
            <Bar dataKey="meetings" fill="#3b82f6" radius={[8, 8, 0, 0]} name="Meetings" />
            <Bar dataKey="messages" fill="#8b5cf6" radius={[8, 8, 0, 0]} name="Messages" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-gradient-to-br from-blue-50 to-white border border-blue-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">16</div>
          <div className="text-sm text-gray-600 mt-1">Meetings</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">256</div>
          <div className="text-sm text-gray-600 mt-1">Messages</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-pink-50 to-white border border-pink-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">12</div>
          <div className="text-sm text-gray-600 mt-1">New contacts</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-green-50 to-white border border-green-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">8h</div>
          <div className="text-sm text-gray-600 mt-1">Social time</div>
        </div>
      </div>

      {/* Top Contacts */}
      <div className="p-6 bg-white border border-gray-200 rounded-xl">
        <h3 className="font-medium text-gray-900 mb-4">Top Contacts</h3>
        <div className="space-y-3">
          {[
            { name: "Sarah Johnson", interactions: 24, avatar: "SJ" },
            { name: "Alex Chen", interactions: 18, avatar: "AC" },
            { name: "Work Team", interactions: 15, avatar: "WT" },
            { name: "Study Group", interactions: 12, avatar: "SG" },
            { name: "Family", interactions: 10, avatar: "FA" },
          ].map((contact, index) => (
            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-900 text-white flex items-center justify-center text-sm font-medium">
                  {contact.avatar}
                </div>
                <span className="text-sm font-medium text-gray-900">{contact.name}</span>
              </div>
              <div className="text-sm text-gray-500">{contact.interactions} interactions</div>
            </div>
          ))}
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
                <div className="text-xs text-gray-500 mt-1">{activity.people}</div>
              </div>
              <div className="text-xs text-gray-400">{activity.date}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}