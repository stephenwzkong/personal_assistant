import { Target, Plus, ListChecks, TrendingUp } from "lucide-react";

interface GoalsTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function GoalsTab({ onQuickAction }: GoalsTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button
          onClick={() => onQuickAction?.("Create a new goal")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-orange-50 text-orange-700 flex items-center justify-center">
            <Target className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Create Goal</div>
            <div className="text-xs text-gray-500">Set a new target</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Update progress on my goals")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-green-50 text-green-700 flex items-center justify-center">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Update Progress</div>
            <div className="text-xs text-gray-500">Log achievements</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Show my active goals and their status")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <ListChecks className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">View Goals</div>
            <div className="text-xs text-gray-500">Check status</div>
          </div>
        </button>
      </div>
    </div>
  );
}
