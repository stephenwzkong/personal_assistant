import { DollarSign, TrendingDown, TrendingUp, Plus } from "lucide-react";

interface FinanceTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function FinanceTab({ onQuickAction }: FinanceTabProps) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button
          onClick={() => onQuickAction?.("Add a new expense")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-red-50 text-red-700 flex items-center justify-center">
            <TrendingDown className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Add Expense</div>
            <div className="text-xs text-gray-500">Log spending</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Log income or earnings")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-green-50 text-green-700 flex items-center justify-center">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">Add Income</div>
            <div className="text-xs text-gray-500">Log earnings</div>
          </div>
          <Plus className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600 transition-colors" />
        </button>

        <button
          onClick={() => onQuickAction?.("Show my current budget status")}
          className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-md transition-all cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <DollarSign className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">View Budget</div>
            <div className="text-xs text-gray-500">Check limits</div>
          </div>
        </button>
      </div>
    </div>
  );
}
