import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, RotateCcw } from "lucide-react";
import { useSession } from "../../hooks/useSession";
import { useChat } from "../../hooks/useChat";
import { useChatContext } from "../../contexts/ChatContext";

export function ChatInterface() {
  const { sessionId, userId, ready } = useSession();
  const { messages, send, clear, isThinking } = useChat(sessionId, userId);
  const { pendingMessage, consumePending } = useChatContext();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle prefilled messages from other pages (quick actions, calendar clicks, etc.)
  useEffect(() => {
    if (pendingMessage) {
      const msg = consumePending();
      setInput(msg);
      inputRef.current?.focus();
    }
  }, [pendingMessage, consumePending]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !ready) return;
    send(input);
    setInput("");
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg text-gray-900">Assistant</h2>
            <p className="text-sm text-gray-500 mt-1">Ask me anything about your day</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clear}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Clear chat history"
            >
              <RotateCcw className="w-4 h-4" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="space-y-6">
          {messages.length === 0 && !isThinking && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-700" />
              </div>
              <div className="flex-1 text-left">
                <div className="inline-block px-4 py-3 rounded-2xl bg-gray-50 text-gray-900">
                  <p className="text-[15px] leading-relaxed">
                    Hi! I can help you manage your calendar, track wellness, log expenses, and more. What would you like to do?
                  </p>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 ${
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
                className={`flex-1 max-w-[85%] ${
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
            <div className="flex gap-4">
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
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Schedule a meeting, log a workout, track spending..."
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-[15px] placeholder:text-gray-400"
            disabled={!ready}
          />
          <button
            type="submit"
            disabled={!input.trim() || !ready}
            className="px-5 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
