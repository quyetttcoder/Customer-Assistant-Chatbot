"use client";
import Conversation from "./components/Conversation";
import { useChatWebsocket } from "./hooks/useChatWebsocket";
import ChatInput from "./components/ChatInput";

export default function Home() {
  const { messages, pending, loading, connected, sendMessage, resolveInterrupt } = useChatWebsocket();

  return (
    <div className="flex h-screen flex-col">
      <div className="min-h-0 flex-1">
        <Conversation
        loading={loading}
        messages={messages}
        pending={pending}
        onResolve={resolveInterrupt}
      />
      </div>
      <div className="flex w-full justify-center my-8">
        <ChatInput
        onSend={sendMessage}
        disable={!connected || loading || !!pending}
        />
      </div>
    </div>
  );
}