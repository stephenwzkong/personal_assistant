import { Activity, Moon, Utensils, Plus } from "lucide-react";

interface WellnessTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function WellnessTab({ onQuickAction }: WellnessTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
    </div>
  );
}
