import { MessageCircle, Calendar, Heart, Plus } from "lucide-react";

interface SocialTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function SocialTab({ onQuickAction }: SocialTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
    </div>
  );
}
