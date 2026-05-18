import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";
import React from "react";
import { ChatProvider } from "../../../src/assistant/frontend/src/contexts/ChatContext";

vi.mock("../../../src/assistant/frontend/src/hooks/useSession", () => ({
  useSession: () => ({ sessionId: "sess", userId: "user", ready: true }),
}));

const mockSend = vi.fn();
const mockClear = vi.fn();

vi.mock("../../../src/assistant/frontend/src/hooks/useChat", () => ({
  useChat: () => ({
    messages: [],
    send: mockSend,
    clear: mockClear,
    isThinking: false,
    error: null,
  }),
}));

import { ChatInterface } from "../../../src/assistant/frontend/src/app/components/ChatInterface";

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

describe("ChatInterface", () => {
  beforeEach(() => {
    mockSend.mockClear();
    mockClear.mockClear();
  });

  it("renders empty state with welcome message", () => {
    render(React.createElement(ChatInterface), { wrapper: Wrapper });
    expect(screen.getByText(/I can help you manage/i)).toBeInTheDocument();
  });

  it("has an input field", () => {
    render(React.createElement(ChatInterface), { wrapper: Wrapper });
    expect(screen.getByPlaceholderText(/Schedule a meeting/i)).toBeInTheDocument();
  });

  it("can type and submit a message", async () => {
    const user = userEvent.setup();
    render(React.createElement(ChatInterface), { wrapper: Wrapper });

    const input = screen.getByPlaceholderText(/Schedule a meeting/i);
    await user.type(input, "Hello assistant");
    await user.keyboard("{Enter}");

    expect(mockSend).toHaveBeenCalledWith("Hello assistant");
  });
});
