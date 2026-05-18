import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { server } from "./setup";
import { useChat } from "../../../src/assistant/frontend/src/hooks/useChat";

function createWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: qc }, children);
}

describe("useChat", () => {
  beforeEach(() => {
    server.use(
      http.post("*/api/chat", () =>
        HttpResponse.json({
          role: "assistant",
          content: "I can help!",
          timestamp: "12:00",
        })
      )
    );
  });

  it("sends message and appends to history", async () => {
    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Hello"));

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Hello");

    await waitFor(() => expect(result.current.messages).toHaveLength(2));
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].content).toBe("I can help!");
  });

  it("sets isThinking during request", async () => {
    server.use(
      http.post("*/api/chat", async () => {
        await new Promise((r) => setTimeout(r, 50));
        return HttpResponse.json({
          role: "assistant",
          content: "Done",
          timestamp: "12:00",
        });
      })
    );

    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Think"));
    expect(result.current.isThinking).toBe(true);

    await waitFor(() => expect(result.current.isThinking).toBe(false));
  });

  it("clear resets history", async () => {
    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Hello"));
    await waitFor(() => expect(result.current.messages).toHaveLength(2));

    act(() => result.current.clear());
    expect(result.current.messages).toHaveLength(0);
  });

  it("handles error response", async () => {
    server.use(
      http.post("*/api/chat", () =>
        new HttpResponse("Server error", { status: 500 })
      )
    );

    const { result } = renderHook(() => useChat("sess", "user"), {
      wrapper: createWrapper(),
    });

    act(() => result.current.send("Fail"));
    await waitFor(() => expect(result.current.error).toBeTruthy());
    expect(result.current.isThinking).toBe(false);
  });
});
