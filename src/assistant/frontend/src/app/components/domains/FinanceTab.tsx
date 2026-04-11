import { DollarSign, TrendingDown, TrendingUp, ShoppingCart, Coffee, Home, Plus } from "lucide-react";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const spendingData = [
  { day: "Mon", amount: 45 },
  { day: "Tue", amount: 32 },
  { day: "Wed", amount: 28 },
  { day: "Thu", amount: 52 },
  { day: "Fri", amount: 38 },
  { day: "Sat", amount: 65 },
  { day: "Sun", amount: 42 },
];

const categoryData = [
  { name: "Food", value: 120, color: "#f59e0b" },
  { name: "Transport", value: 45, color: "#3b82f6" },
  { name: "Shopping", value: 85, color: "#8b5cf6" },
  { name: "Bills", value: 150, color: "#10b981" },
  { name: "Entertainment", value: 40, color: "#ec4899" },
];

interface Transaction {
  date: string;
  description: string;
  amount: number;
  category: string;
}

const recentTransactions: Transaction[] = [
  { date: "Today, 1:30 PM", description: "Lunch at cafe", amount: -15.50, category: "Food" },
  { date: "Today, 9:00 AM", description: "Coffee", amount: -5.20, category: "Food" },
  { date: "Yesterday, 6:00 PM", description: "Groceries", amount: -42.80, category: "Food" },
  { date: "Yesterday, 3:00 PM", description: "Uber ride", amount: -12.00, category: "Transport" },
  { date: "Mar 14", description: "Salary deposit", amount: 2500.00, category: "Income" },
];

interface FinanceTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function FinanceTab({ onQuickAction }: FinanceTabProps) {
  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="grid grid-cols-3 gap-4">
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

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="p-6 bg-white border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-medium text-gray-900">Daily Spending</h3>
              <p className="text-sm text-gray-500 mt-1">Last 7 days</p>
            </div>
            <div className="text-sm font-medium text-gray-900">$302 total</div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={spendingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="day" stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
              <Tooltip />
              <Bar dataKey="amount" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="p-6 bg-white border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-medium text-gray-900">Spending by Category</h3>
              <p className="text-sm text-gray-500 mt-1">This month</p>
            </div>
            <div className="text-sm font-medium text-gray-900">$440</div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {categoryData.map((cat, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }}></div>
                <span className="text-xs text-gray-600">{cat.name}: ${cat.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-gradient-to-br from-green-50 to-white border border-green-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">$2,500</div>
          <div className="text-sm text-gray-600 mt-1">Monthly income</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-red-50 to-white border border-red-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">$1,240</div>
          <div className="text-sm text-gray-600 mt-1">Month spending</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-blue-50 to-white border border-blue-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">$1,260</div>
          <div className="text-sm text-gray-600 mt-1">Remaining</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">50%</div>
          <div className="text-sm text-gray-600 mt-1">Savings rate</div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="p-6 bg-white border border-gray-200 rounded-xl">
        <h3 className="font-medium text-gray-900 mb-4">Recent Transactions</h3>
        <div className="space-y-3">
          {recentTransactions.map((transaction, index) => (
            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-900">{transaction.description}</span>
                  <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{transaction.category}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">{transaction.date}</div>
              </div>
              <div className={`text-sm font-medium ${transaction.amount > 0 ? 'text-green-600' : 'text-gray-900'}`}>
                {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}