import { Clock, BookOpen, Code, Plus } from "lucide-react";

interface ProductivityTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function ProductivityTab({ onQuickAction }: ProductivityTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
    </div>
  );
}
