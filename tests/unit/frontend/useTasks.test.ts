import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { server } from "./setup";
import { useTasks, useMoveTask, useDeleteTask } from "../../../src/assistant/frontend/src/hooks/useTasks";

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe("useTasks", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/tasks", () =>
        HttpResponse.json({
          tasks: [
            {
              task_id: "t1",
              parent_task_id: "",
              title: "Test Task",
              description: "",
              status: "todo",
              priority: "medium",
              category: "",
              due_date: "",
              position: 0,
              created_at: "",
              updated_at: "",
            },
          ],
          count: 1,
        })
      )
    );
  });

  it("fetches tasks", async () => {
    const { result } = renderHook(() => useTasks(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data!.tasks).toHaveLength(1);
    expect(result.current.data!.tasks[0].title).toBe("Test Task");
  });
});

describe("useMoveTask", () => {
  it("calls PATCH with status", async () => {
    let capturedBody: any;
    server.use(
      http.patch("*/api/tasks/:id/status", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({ status: "success" });
      })
    );

    const { result } = renderHook(() => useMoveTask(), { wrapper: createWrapper() });

    act(() => result.current.mutate({ taskId: "t1", status: "in_progress" }));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(capturedBody.status).toBe("in_progress");
  });
});

describe("useDeleteTask", () => {
  it("calls DELETE", async () => {
    let deletedId: string = "";
    server.use(
      http.delete("*/api/tasks/:id", ({ params }) => {
        deletedId = params.id as string;
        return HttpResponse.json({ status: "success" });
      })
    );

    const { result } = renderHook(() => useDeleteTask(), { wrapper: createWrapper() });

    act(() => result.current.mutate("t1"));
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(deletedId).toBe("t1");
  });
});
