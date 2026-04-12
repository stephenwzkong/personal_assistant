import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, RotateCcw } from "lucide-react";
import { useSession } from "../../hooks/useSession";
import { useChat } from "../../hooks/useChat";
import { useChatContext } from "../../contexts/ChatContext";
import { useSearchParams } from "react-router";

const suggestions = [
  "Schedule a meeting tomorrow at 2pm",
  "Log a 30-minute run",
  "Add expense: lunch $12",
  "How did I sleep this week?",
];

export function ChatPage() {
  const { sessionId, userId, ready } = useSession();
  const { messages, send, clear, isThinking } = useChat(sessionId, userId);
  const { pendingMessage, consumePending } = useChatContext();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [searchParams, setSearchParams] = useSearchParams();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle prefilled messages from dashboard quick actions
  useEffect(() => {
    if (pendingMessage) {
      const msg = consumePending();
      setInput(msg);
      inputRef.current?.focus();
    }
  }, [pendingMessage, consumePending]);

  // Handle query param prefill (e.g., /?q=Log+a+workout)
  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      setInput(q);
      setSearchParams({}, { replace: true });
      inputRef.current?.focus();
    }
  }, [searchParams, setSearchParams]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !ready) return;
    send(input);
    setInput("");
  };

  const handleSuggestion = (text: string) => {
    if (!ready) return;
    send(text);
  };

  const isEmpty = messages.length === 0 && !isThinking;

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {isEmpty ? (
          /* Empty state — centered like Claude Desktop */
          <div className="h-full flex flex-col items-center justify-center px-6">
            <div className="w-12 h-12 rounded-2xl bg-gray-900 flex items-center justify-center mb-6">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-xl text-gray-900 mb-2">What can I help you with?</h2>
            <p className="text-sm text-gray-500 mb-8 text-center max-w-md">
              I can manage your calendar, track wellness, log expenses, and help you stay organized.
            </p>
            <div className="flex flex-wrap justify-center gap-2 max-w-lg">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSuggestion(s)}
                  className="px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-100 hover:border-gray-300 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Conversation */
          <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === "user"
                      ? "bg-gray-900"
                      : "bg-gray-100 border border-gray-200"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-gray-700" />
                  )}
                </div>
                <div
                  className={`flex-1 max-w-[80%] ${
                    message.role === "user" ? "text-right" : "text-left"
                  }`}
                >
                  <div
                    className={`inline-block px-4 py-3 rounded-2xl ${
                      message.role === "user"
                        ? "bg-gray-900 text-white"
                        : "bg-gray-50 text-gray-900"
                    }`}
                  >
                    <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
                      {message.content}
                    </p>
                  </div>
                </div>
              </div>
            ))}

            {isThinking && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-gray-700" />
                </div>
                <div className="flex-1">
                  <div className="inline-block px-4 py-3 rounded-2xl bg-gray-50 border border-gray-100">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input bar — pinned to bottom */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            {messages.length > 0 && (
              <button
                type="button"
                onClick={clear}
                className="px-3 py-3 text-gray-400 hover:text-gray-600 rounded-xl hover:bg-gray-50 transition-colors"
                title="New conversation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            )}
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message your assistant..."
              className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-[15px] placeholder:text-gray-400"
              disabled={!ready}
              autoFocus
            />
            <button
              type="submit"
              disabled={!input.trim() || !ready}
              className="px-4 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
