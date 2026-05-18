import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import React from "react";
import { ChatProvider } from "../../../src/assistant/frontend/src/contexts/ChatContext";

const mockTasks = [
  { task_id: "t1", parent_task_id: "", title: "Todo Item", description: "", status: "todo", priority: "high", category: "school", due_date: "2026-05-20", position: 0, created_at: "", updated_at: "" },
  { task_id: "t2", parent_task_id: "", title: "In Progress Item", description: "", status: "in_progress", priority: "medium", category: "", due_date: "", position: 1, created_at: "", updated_at: "" },
  { task_id: "t3", parent_task_id: "", title: "Done Item", description: "", status: "done", priority: "low", category: "", due_date: "", position: 2, created_at: "", updated_at: "" },
];

vi.mock("../../../src/assistant/frontend/src/hooks/useTasks", () => ({
  useTasks: () => ({
    data: { tasks: mockTasks, count: 3 },
    isLoading: false,
    error: null,
  }),
  useMoveTask: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteTask: () => ({ mutate: vi.fn(), isPending: false }),
}));

import { TasksPage } from "../../../src/assistant/frontend/src/app/components/TasksPage";

function Wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient();
  return React.createElement(
    QueryClientProvider,
    { client: qc },
    React.createElement(
      MemoryRouter,
      null,
      React.createElement(ChatProvider, null, children)
    )
  );
}

describe("TasksPage", () => {
  it("renders 3 kanban columns", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("To Do")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByText("Done")).toBeInTheDocument();
  });

  it("displays task cards in correct columns", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("Todo Item")).toBeInTheDocument();
    expect(screen.getByText("In Progress Item")).toBeInTheDocument();
    expect(screen.getByText("Done Item")).toBeInTheDocument();
  });

  it("shows task metadata", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("High")).toBeInTheDocument();
    expect(screen.getByText("school")).toBeInTheDocument();
  });

  it("shows total count", () => {
    render(React.createElement(TasksPage), { wrapper: Wrapper });
    expect(screen.getByText("3 total tasks")).toBeInTheDocument();
  });
});
