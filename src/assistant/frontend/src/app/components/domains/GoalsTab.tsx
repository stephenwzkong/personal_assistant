import { Target, TrendingUp, CheckCircle2, Circle, Plus } from "lucide-react";
import { Progress } from "../ui/progress";

interface Goal {
  id: number;
  title: string;
  description: string;
  progress: number;
  target: number;
  unit: string;
  category: string;
  deadline: string;
  color: string;
}

const goals: Goal[] = [
  {
    id: 1,
    title: "Workout 5 times per week",
    description: "Maintain fitness routine",
    progress: 3,
    target: 5,
    unit: "workouts",
    category: "Wellness",
    deadline: "Weekly",
    color: "green",
  },
  {
    id: 2,
    title: "Study 20 hours per week",
    description: "CS course preparation",
    progress: 12,
    target: 20,
    unit: "hours",
    category: "Productivity",
    deadline: "Weekly",
    color: "blue",
  },
  {
    id: 3,
    title: "Save $500 this month",
    description: "Emergency fund building",
    progress: 240,
    target: 500,
    unit: "dollars",
    category: "Finance",
    deadline: "Mar 31",
    color: "purple",
  },
  {
    id: 4,
    title: "Meet 3 new people",
    description: "Expand network",
    progress: 1,
    target: 3,
    unit: "people",
    category: "Social",
    deadline: "This month",
    color: "pink",
  },
  {
    id: 5,
    title: "Sleep 7+ hours daily",
    description: "Improve sleep quality",
    progress: 5,
    target: 7,
    unit: "days",
    category: "Wellness",
    deadline: "Weekly",
    color: "indigo",
  },
];

interface Milestone {
  date: string;
  title: string;
  category: string;
  achieved: boolean;
}

const recentMilestones: Milestone[] = [
  { date: "Today", title: "Completed 3-day workout streak", category: "Wellness", achieved: true },
  { date: "Yesterday", title: "Finished project milestone", category: "Productivity", achieved: true },
  { date: "Mar 14", title: "Reached 50% savings goal", category: "Finance", achieved: true },
  { date: "Mar 12", title: "Connected with 2 alumni", category: "Social", achieved: true },
  { date: "Mar 10", title: "Maintained sleep schedule for 5 days", category: "Wellness", achieved: true },
];

interface GoalsTabProps {
  onQuickAction?: (prompt: string) => void;
}

export function GoalsTab({ onQuickAction }: GoalsTabProps) {
  const getColorClasses = (color: string) => {
    const colors: { [key: string]: { bg: string; text: string; border: string } } = {
      green: { bg: "bg-green-50", text: "text-green-700", border: "border-green-100" },
      blue: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-100" },
      purple: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-100" },
      pink: { bg: "bg-pink-50", text: "text-pink-700", border: "border-pink-100" },
      indigo: { bg: "bg-indigo-50", text: "text-indigo-700", border: "border-indigo-100" },
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Quick Action */}
      <button
        onClick={() => onQuickAction?.("Create a new goal")}
        className="w-full flex items-center justify-center gap-3 p-4 bg-gradient-to-r from-gray-900 to-gray-800 text-white rounded-xl hover:from-gray-800 hover:to-gray-700 transition-all cursor-pointer group"
      >
        <Plus className="w-5 h-5 group-hover:scale-110 transition-transform" />
        <span>Create New Goal</span>
      </button>

      {/* Active Goals */}
      <div>
        <h2 className="text-sm font-medium text-gray-700 mb-4 uppercase tracking-wide">Active Goals</h2>
        <div className="space-y-4">
          {goals.map((goal) => {
            const percentage = (goal.progress / goal.target) * 100;
            const colorClasses = getColorClasses(goal.color);
            
            return (
              <div
                key={goal.id}
                className={`p-5 bg-white border ${colorClasses.border} rounded-xl hover:shadow-md transition-all`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-gray-900">{goal.title}</h3>
                      <span className={`px-2 py-0.5 text-xs ${colorClasses.bg} ${colorClasses.text} rounded`}>
                        {goal.category}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">{goal.description}</p>
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-xl font-medium text-gray-900">
                      {goal.progress}/{goal.target}
                    </div>
                    <div className="text-xs text-gray-500">{goal.unit}</div>
                  </div>
                </div>
                
                <div className="mb-3">
                  <Progress value={percentage} className="h-2" />
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Deadline: {goal.deadline}</span>
                  <span className={`font-medium ${colorClasses.text}`}>
                    {percentage.toFixed(0)}% complete
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-gradient-to-br from-green-50 to-white border border-green-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">5</div>
          <div className="text-sm text-gray-600 mt-1">Active goals</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-blue-50 to-white border border-blue-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">12</div>
          <div className="text-sm text-gray-600 mt-1">Completed</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-purple-50 to-white border border-purple-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">68%</div>
          <div className="text-sm text-gray-600 mt-1">Avg progress</div>
        </div>
        <div className="p-4 bg-gradient-to-br from-orange-50 to-white border border-orange-100 rounded-xl">
          <div className="text-2xl font-medium text-gray-900">3</div>
          <div className="text-sm text-gray-600 mt-1">Due this week</div>
        </div>
      </div>

      {/* Recent Milestones */}
      <div className="p-6 bg-white border border-gray-200 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-gray-700" />
          <h3 className="font-medium text-gray-900">Recent Milestones</h3>
        </div>
        <div className="space-y-3">
          {recentMilestones.map((milestone, index) => (
            <div key={index} className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="flex-shrink-0 mt-0.5">
                {milestone.achieved ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-300" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">{milestone.title}</span>
                  <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                    {milestone.category}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">{milestone.date}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Motivational Card */}
      <div className="p-6 bg-gradient-to-br from-gray-900 to-gray-800 text-white rounded-xl">
        <div className="flex items-center gap-3 mb-3">
          <Target className="w-6 h-6" />
          <h3 className="font-medium text-lg">Keep Going!</h3>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">
          You're making great progress across all your goals. Stay consistent, and you'll achieve 
          everything you've set out to accomplish this week!
        </p>
        <div className="mt-4 flex items-center gap-4">
          <div className="flex-1 bg-white/10 rounded-full h-2">
            <div className="bg-white rounded-full h-2" style={{ width: '68%' }}></div>
          </div>
          <span className="text-sm font-medium">68% overall</span>
        </div>
      </div>
    </div>
  );
}