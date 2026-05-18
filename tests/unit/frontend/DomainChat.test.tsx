import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";

vi.mock("../../../src/assistant/frontend/src/hooks/useSession", () => ({
  useSession: () => ({ sessionId: "sess", userId: "user", ready: true }),
}));

const mockSend = vi.fn();
vi.mock("../../../src/assistant/frontend/src/hooks/useChat", () => ({
  useDomainChat: () => ({
    messages: [],
    send: mockSend,
    clear: vi.fn(),
    isThinking: false,
    error: null,
  }),
}));

import { DomainChat } from "../../../src/assistant/frontend/src/app/components/DomainChat";

describe("DomainChat", () => {
  beforeEach(() => {
    mockSend.mockClear();
  });

  it("renders domain-specific header", () => {
    render(React.createElement(DomainChat, { domain: "wellness" }));
    expect(screen.getByText("Wellness Assistant")).toBeInTheDocument();
  });

  it("shows quick action examples", () => {
    render(React.createElement(DomainChat, { domain: "wellness" }));
    expect(screen.getByText("Log a 45-minute run")).toBeInTheDocument();
  });

  it("clicking example sends domain message", async () => {
    const user = userEvent.setup();
    render(React.createElement(DomainChat, { domain: "wellness" }));

    await user.click(screen.getByText("Log a 45-minute run"));
    expect(mockSend).toHaveBeenCalledWith("Log a 45-minute run");
  });

  it("renders different domain configs", () => {
    render(React.createElement(DomainChat, { domain: "finance" }));
    expect(screen.getByText("Finance Assistant")).toBeInTheDocument();
    expect(screen.getByText(/Add expense/)).toBeInTheDocument();
  });
});
