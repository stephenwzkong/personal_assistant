import { useState, useEffect } from "react";
import { initSession } from "../lib/api";

interface SessionState {
  sessionId: string;
  userId: string;
  ready: boolean;
}

export function useSession(): SessionState {
  const [state, setState] = useState<SessionState>({
    sessionId: "",
    userId: "",
    ready: false,
  });

  useEffect(() => {
    // Restore from sessionStorage or create new
    const stored = sessionStorage.getItem("pa_session");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setState({ sessionId: parsed.session_id, userId: parsed.user_id, ready: true });
        return;
      } catch {
        // fall through to init
      }
    }

    initSession().then((s) => {
      sessionStorage.setItem("pa_session", JSON.stringify(s));
      setState({ sessionId: s.session_id, userId: s.user_id, ready: true });
    });
  }, []);

  return state;
}
