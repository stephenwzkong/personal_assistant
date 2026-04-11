import { useState, useCallback } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { sendMessage as apiSendMessage, sendDomainMessage as apiSendDomainMessage } from "../lib/api";
import type { ChatResponse } from "../lib/api";

export interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function useChat(sessionId: string, userId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const qc = useQueryClient();

  const mutation = useMutation<ChatResponse, Error, string>({
    mutationFn: (message: string) => apiSendMessage(sessionId, userId, message),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          content: data.content,
          timestamp: new Date(),
        },
      ]);
      // Refresh calendar after agent response
      qc.invalidateQueries({ queryKey: ["calendarGrid"] });
      qc.invalidateQueries({ queryKey: ["calendarEvents"] });
    },
  });

  const send = useCallback(
    (text: string) => {
      if (!text.trim()) return;
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: "user", content: text, timestamp: new Date() },
      ]);
      mutation.mutate(text);
    },
    [mutation],
  );

  const clear = useCallback(() => setMessages([]), []);

  return {
    messages,
    send,
    clear,
    isThinking: mutation.isPending,
    error: mutation.error,
  };
}

export function useDomainChat(sessionId: string, userId: string, domain: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const qc = useQueryClient();

  const mutation = useMutation<ChatResponse, Error, string>({
    mutationFn: (message: string) => apiSendDomainMessage(sessionId, userId, message, domain),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          content: data.content,
          timestamp: new Date(),
        },
      ]);
      qc.invalidateQueries({ queryKey: ["calendarGrid"] });
    },
  });

  const send = useCallback(
    (text: string) => {
      if (!text.trim()) return;
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), role: "user", content: text, timestamp: new Date() },
      ]);
      mutation.mutate(text);
    },
    [mutation],
  );

  const clear = useCallback(() => setMessages([]), []);

  return {
    messages,
    send,
    clear,
    isThinking: mutation.isPending,
    error: mutation.error,
  };
}
