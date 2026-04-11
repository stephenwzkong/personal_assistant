import { useState, useRef, useEffect } from "react";
import { Send, Activity, Briefcase, DollarSign, Users, Target, RotateCcw } from "lucide-react";
import { useSession } from "../../hooks/useSession";
import { useDomainChat } from "../../hooks/useChat";

interface DomainChatProps {
  domain: string;
  externalInput?: string;
  onInputUsed?: () => void;
}

const domainConfig = {
  wellness: {
    name: "Wellness",
    icon: Activity,
    color: "text-green-700",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
    examples: [
      "Log a 45-minute run",
      "How many hours did I sleep this week?",
      "Set a reminder to drink water",
    ],
  },
  productivity: {
    name: "Productivity",
    icon: Briefcase,
    color: "text-blue-700",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
    examples: [
      "Add 3 hours of study time",
      "What's my focus time trend?",
      "Schedule a deep work session",
    ],
  },
  finance: {
    name: "Finance",
    icon: DollarSign,
    color: "text-purple-700",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200",
    examples: [
      "Add expense: lunch $15",
      "How much have I spent this week?",
      "Set budget for groceries",
    ],
  },
  social: {
    name: "Social",
    icon: Users,
    color: "text-pink-700",
    bgColor: "bg-pink-50",
    borderColor: "border-pink-200",
    examples: [
      "Log coffee meeting with Sarah",
      "Show my top contacts",
      "Schedule a team lunch",
    ],
  },
  goals: {
    name: "Goals",
    icon: Target,
    color: "text-orange-700",
    bgColor: "bg-orange-50",
    borderColor: "border-orange-200",
    examples: [
      "Create goal: read 2 books this month",
      "Update workout goal progress",
      "Show goals due this week",
    ],
  },
};

export function DomainChat({ domain, externalInput, onInputUsed }: DomainChatProps) {
  const { sessionId, userId, ready } = useSession();
  const { messages, send, clear, isThinking } = useDomainChat(sessionId, userId, domain);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const config = domainConfig[domain as keyof typeof domainConfig] || domainConfig.wellness;
  const Icon = config.icon;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle external input from quick actions
  useEffect(() => {
    if (externalInput && ready) {
      send(externalInput);
      if (onInputUsed) {
        onInputUsed();
      }
    }
  }, [externalInput, ready]);

  // Reset messages when domain changes
  useEffect(() => {
    clear();
  }, [domain]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !ready) return;
    send(input);
    setInput("");
  };

  const handleExampleClick = (example: string) => {
    if (!ready) return;
    send(example);
  };

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200">
      {/* Header */}
      <div className={`p-4 border-b border-gray-200 ${config.bgColor}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg ${config.bgColor} ${config.color} flex items-center justify-center border ${config.borderColor}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-gray-900">{config.name} Assistant</h2>
              <p className="text-xs text-gray-500">Domain-specific AI helper</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clear}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white/50 rounded-lg transition-colors"
              title="Clear chat"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isThinking && (
          <div className="mb-6">
            <p className="text-sm text-gray-500 mb-3">Try asking:</p>
            <div className="space-y-2">
              {config.examples.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="block w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-gray-700"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${
                message.role === "user"
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-900 border border-gray-200"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}

        {isThinking && (
          <div className="flex justify-start">
            <div className="bg-gray-100 border border-gray-200 rounded-2xl px-4 py-2.5">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask about ${config.name.toLowerCase()}...`}
            className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent text-sm"
            ref={inputRef}
            disabled={!ready}
          />
          <button
            type="submit"
            disabled={!input.trim() || !ready}
            className="px-4 py-2.5 bg-gray-900 text-white rounded-xl hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
