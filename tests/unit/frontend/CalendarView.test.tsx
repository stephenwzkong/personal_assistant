import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import React from "react";
import { ChatProvider } from "../../../src/assistant/frontend/src/contexts/ChatContext";

vi.mock("../../../src/assistant/frontend/src/hooks/useCalendar", () => ({
  useCalendarEvents: () => ({
    data: { events: [], count: 0 },
    isLoading: false,
  }),
}));

import { CalendarView } from "../../../src/assistant/frontend/src/app/components/CalendarView";

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

describe("CalendarView", () => {
  it("renders calendar with view buttons", () => {
    render(React.createElement(CalendarView), { wrapper: Wrapper });
    // react-big-calendar also renders these labels, so use getAllByText
    expect(screen.getAllByText("Day").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Week").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Month").length).toBeGreaterThan(0);
  });

  it("has Today button", () => {
    render(React.createElement(CalendarView), { wrapper: Wrapper });
    expect(screen.getByRole("button", { name: "Today" })).toBeInTheDocument();
  });

  it("shows month/year header", () => {
    render(React.createElement(CalendarView), { wrapper: Wrapper });
    const now = new Date();
    const monthYear = now.toLocaleDateString("en-US", { month: "long", year: "numeric" });
    expect(screen.getByText(monthYear)).toBeInTheDocument();
  });
});
