import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "./setup";
import { useSession } from "../../../src/assistant/frontend/src/hooks/useSession";

describe("useSession", () => {
  beforeEach(() => {
    sessionStorage.clear();
    server.use(
      http.post("*/api/session/init", () =>
        HttpResponse.json({ session_id: "new-sess", user_id: "default_user" })
      )
    );
  });

  it("initializes session on mount", async () => {
    const { result } = renderHook(() => useSession());

    await waitFor(() => {
      expect(result.current.ready).toBe(true);
    });
    expect(result.current.sessionId).toBe("new-sess");
    expect(result.current.userId).toBe("default_user");
  });

  it("persists to sessionStorage", async () => {
    const { result } = renderHook(() => useSession());

    await waitFor(() => expect(result.current.ready).toBe(true));
    const stored = JSON.parse(sessionStorage.getItem("pa_session")!);
    expect(stored.session_id).toBe("new-sess");
  });

  it("returns existing session from sessionStorage", async () => {
    sessionStorage.setItem(
      "pa_session",
      JSON.stringify({ session_id: "cached-sess", user_id: "cached-user" })
    );

    const { result } = renderHook(() => useSession());

    await waitFor(() => expect(result.current.ready).toBe(true));
    expect(result.current.sessionId).toBe("cached-sess");
    expect(result.current.userId).toBe("cached-user");
  });
});
