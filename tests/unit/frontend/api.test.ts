import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "./setup";
import {
  initSession,
  sendMessage,
  sendDomainMessage,
  getCalendarGrid,
  getTasks,
} from "../../../src/assistant/frontend/src/lib/api";

describe("API client", () => {
  describe("initSession", () => {
    it("calls POST /api/session/init", async () => {
      server.use(
        http.post("*/api/session/init", () =>
          HttpResponse.json({ session_id: "s-1", user_id: "u-1" })
        )
      );
      const result = await initSession();
      expect(result.session_id).toBe("s-1");
      expect(result.user_id).toBe("u-1");
    });
  });

  describe("sendMessage", () => {
    it("sends sessionId, userId, message in body", async () => {
      let capturedBody: any;
      server.use(
        http.post("*/api/chat", async ({ request }) => {
          capturedBody = await request.json();
          return HttpResponse.json({
            role: "assistant",
            content: "Hello!",
            timestamp: "12:00",
          });
        })
      );
      const result = await sendMessage("sess", "user", "hi");
      expect(capturedBody).toEqual({
        session_id: "sess",
        user_id: "user",
        message: "hi",
      });
      expect(result.content).toBe("Hello!");
    });
  });

  describe("sendDomainMessage", () => {
    it("includes domain field", async () => {
      let capturedBody: any;
      server.use(
        http.post("*/api/chat/domain", async ({ request }) => {
          capturedBody = await request.json();
          return HttpResponse.json({
            role: "assistant",
            content: "OK",
            timestamp: "12:00",
          });
        })
      );
      await sendDomainMessage("sess", "user", "run", "wellness");
      expect(capturedBody.domain).toBe("wellness");
    });
  });

  describe("getCalendarGrid", () => {
    it("passes week_start as query param", async () => {
      let capturedUrl: string = "";
      server.use(
        http.get("*/api/calendar/grid", ({ request }) => {
          capturedUrl = request.url;
          return HttpResponse.json({
            grid: [],
            week_label: "May 2026",
            event_count: 0,
          });
        })
      );
      await getCalendarGrid("2026-05-11");
      expect(capturedUrl).toContain("week_start=2026-05-11");
    });
  });

  describe("getTasks", () => {
    it("returns typed response", async () => {
      server.use(
        http.get("*/api/tasks", () =>
          HttpResponse.json({
            tasks: [
              {
                task_id: "t1",
                parent_task_id: "",
                title: "Test",
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
      const result = await getTasks();
      expect(result.tasks).toHaveLength(1);
      expect(result.tasks[0].task_id).toBe("t1");
    });
  });

  describe("error handling", () => {
    it("throws on fetch failure", async () => {
      server.use(
        http.post("*/api/chat", () =>
          new HttpResponse("Server Error", { status: 500 })
        )
      );
      await expect(sendMessage("s", "u", "msg")).rejects.toThrow();
    });
  });
});
