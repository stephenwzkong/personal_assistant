import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

interface ChatContextType {
  pendingMessage: string;
  prefillChat: (msg: string) => void;
  consumePending: () => string;
}

const ChatContext = createContext<ChatContextType>({
  pendingMessage: "",
  prefillChat: () => {},
  consumePending: () => "",
});

export function ChatProvider({ children }: { children: ReactNode }) {
  const [pendingMessage, setPendingMessage] = useState("");

  const prefillChat = useCallback((msg: string) => {
    setPendingMessage(msg);
  }, []);

  const consumePending = useCallback(() => {
    const msg = pendingMessage;
    setPendingMessage("");
    return msg;
  }, [pendingMessage]);

  return (
    <ChatContext.Provider value={{ pendingMessage, prefillChat, consumePending }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  return useContext(ChatContext);
}
