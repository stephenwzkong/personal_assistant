import { useMemo } from "react";
import { useNavigate } from "react-router";
import {
  CircleDot, Clock, CheckCircle2, Trash2, ChevronRight, ChevronLeft,
  AlertCircle, ArrowUp, ArrowRight, ArrowDown, Calendar,
} from "lucide-react";
import { useTasks, useMoveTask, useDeleteTask } from "../../hooks/useTasks";
import { useChatContext } from "../../contexts/ChatContext";
import type { TaskOut } from "../../lib/api";

const COLUMNS = [
  { key: "todo", label: "To Do", icon: CircleDot, color: "text-gray-600", bgColor: "bg-gray-50", borderColor: "border-gray-200" },
  { key: "in_progress", label: "In Progress", icon: Clock, color: "text-blue-600", bgColor: "bg-blue-50", borderColor: "border-blue-200" },
  { key: "done", label: "Done", icon: CheckCircle2, color: "text-green-600", bgColor: "bg-green-50", borderColor: "border-green-200" },
] as const;

const PRIORITY_CONFIG = {
  high: { icon: ArrowUp, color: "text-red-600", label: "High" },
  medium: { icon: ArrowRight, color: "text-orange-500", label: "Medium" },
  low: { icon: ArrowDown, color: "text-gray-400", label: "Low" },
} as const;

const NEXT_STATUS: Record<string, string> = {
  todo: "in_progress",
  in_progress: "done",
};

const PREV_STATUS: Record<string, string> = {
  in_progress: "todo",
  done: "in_progress",
};

function TaskCard({ task, childCount }: { task: TaskOut; childCount: number }) {
  const move = useMoveTask();
  const remove = useDeleteTask();
  const priority = PRIORITY_CONFIG[task.priority as keyof typeof PRIORITY_CONFIG] || PRIORITY_CONFIG.medium;
  const PriorityIcon = priority.icon;
  const nextStatus = NEXT_STATUS[task.status];
  const prevStatus = PREV_STATUS[task.status];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow group">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="text-sm font-medium text-gray-900 flex-1">{task.title}</h3>
        <button
          onClick={() => remove.mutate(task.task_id)}
          className="p-1 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
          title="Delete task"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {task.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">{task.description}</p>
      )}

      <div className="flex items-center gap-2 flex-wrap mb-2">
        <span className={`flex items-center gap-1 text-xs ${priority.color}`}>
          <PriorityIcon className="w-3 h-3" />
          {priority.label}
        </span>
        {task.category && (
          <span className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">
            {task.category}
          </span>
        )}
        {task.due_date && (
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Calendar className="w-3 h-3" />
            {task.due_date}
          </span>
        )}
        {childCount > 0 && (
          <span className="text-xs text-gray-400">{childCount} steps</span>
        )}
      </div>

      <div className="flex items-center gap-1">
        {prevStatus && (
          <button
            onClick={() => move.mutate({ taskId: task.task_id, status: prevStatus })}
            disabled={move.isPending}
            className="flex items-center gap-1 px-2 py-1 text-xs text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50"
          >
            <ChevronLeft className="w-3 h-3" />
          </button>
        )}
        {nextStatus && (
          <button
            onClick={() => move.mutate({ taskId: task.task_id, status: nextStatus })}
            disabled={move.isPending}
            className="flex items-center gap-1 px-2 py-1 text-xs text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50"
          >
            <ChevronRight className="w-3 h-3" />
          </button>
        )}
      </div>
    </div>
  );
}

export function TasksPage() {
  const { data, isLoading, error } = useTasks();
  const { prefillChat } = useChatContext();
  const navigate = useNavigate();

  const { columns, childCounts } = useMemo(() => {
    const tasks = data?.tasks || [];
    const grouped: Record<string, TaskOut[]> = { todo: [], in_progress: [], done: [] };
    const counts: Record<string, number> = {};

    for (const t of tasks) {
      if (t.parent_task_id) {
        counts[t.parent_task_id] = (counts[t.parent_task_id] || 0) + 1;
      }
    }

    // Show parent tasks and orphan sub-tasks (whose parent doesn't exist)
    const parentIds = new Set(tasks.filter((t) => !t.parent_task_id).map((t) => t.task_id));
    for (const t of tasks) {
      if (!t.parent_task_id || !parentIds.has(t.parent_task_id)) {
        if (grouped[t.status]) {
          grouped[t.status].push(t);
        }
      }
    }

    return { columns: grouped, childCounts: counts };
  }, [data]);

  const handleNewTask = () => {
    prefillChat("I need to add a new to-do: ");
    navigate("/");
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl text-gray-900">Tasks</h1>
            <p className="text-sm text-gray-500 mt-1">
              {data ? `${data.count} total tasks` : "Loading..."}
            </p>
          </div>
          <button
            onClick={handleNewTask}
            className="px-4 py-2 bg-gray-900 text-white text-sm rounded-lg hover:bg-gray-800 transition-colors"
          >
            + New Task
          </button>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto p-6">
        {error ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">Failed to load tasks</span>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="w-6 h-6 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-6 h-full min-w-[720px]">
            {COLUMNS.map((col) => {
              const Icon = col.icon;
              const tasks = columns[col.key] || [];
              return (
                <div key={col.key} className="flex flex-col min-h-0">
                  {/* Column Header */}
                  <div className={`flex items-center gap-2 px-3 py-2 ${col.bgColor} rounded-lg mb-3`}>
                    <Icon className={`w-4 h-4 ${col.color}`} />
                    <span className={`text-sm font-medium ${col.color}`}>{col.label}</span>
                    <span className="text-xs text-gray-400 ml-auto">{tasks.length}</span>
                  </div>

                  {/* Cards */}
                  <div className="flex-1 space-y-2 overflow-y-auto pr-1">
                    {tasks.length === 0 ? (
                      <div className="text-center py-8 text-xs text-gray-400">
                        No tasks
                      </div>
                    ) : (
                      tasks.map((task) => (
                        <TaskCard
                          key={task.task_id}
                          task={task}
                          childCount={childCounts[task.task_id] || 0}
                        />
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
