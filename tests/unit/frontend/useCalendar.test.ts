import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { server } from "./setup";
import { useCalendarGrid } from "../../../src/assistant/frontend/src/hooks/useCalendar";

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

const mockGrid = {
  grid: Array.from({ length: 6 }, () =>
    Array.from({ length: 7 }, (_, i) => ({
      date: `2026-05-1${i}`,
      day_num: String(10 + i),
      is_today: i === 0,
      events: [],
    }))
  ),
  week_label: "May - June 2026",
  event_count: 0,
};

describe("useCalendarGrid", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/calendar/grid", () => HttpResponse.json(mockGrid))
    );
  });

  it("fetches grid on mount", async () => {
    const { result } = renderHook(() => useCalendarGrid(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.data).toBeDefined());
    expect(result.current.data!.grid).toHaveLength(6);
    expect(result.current.data!.grid[0]).toHaveLength(7);
  });

  it("navigateWeek changes weekStart", async () => {
    const { result } = renderHook(() => useCalendarGrid(), {
      wrapper: createWrapper(),
    });

    const initial = result.current.weekStart;
    act(() => result.current.navigateWeek(1));
    expect(result.current.weekStart).not.toBe(initial);
  });
});
