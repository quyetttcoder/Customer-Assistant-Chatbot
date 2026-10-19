import React, { useEffect, useRef } from "react";
import { TypeAnimation } from "react-type-animation";

import { InterruptPayload, ChatMessage } from "./type";


export interface ConversationProps {
  messages: ChatMessage[];
  loading: boolean;
  pending: InterruptPayload | null;
  onResolve: (approved: "yes" | "no") => void;
}

const OPTION_LABEL: Record<string, string> = {
  yes: "Approve",
  no: "Deny"
}

export default function Conversation({
  messages,
  pending,
  loading,
  onResolve
}: ConversationProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  let isStreamingText = false;
  if (messages.length > 0) {
    const lastMessage = messages[messages.length - 1];
    isStreamingText = lastMessage.role === "assistant" && !!lastMessage.stream && !!lastMessage.content;
  }
  const showThinking = loading && !isStreamingText;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({behavior: "smooth"});
  }, [messages, pending, showThinking])

  const handleChatLength = (message: string) => {
    return message.split(" ").map((word, index) => {
      if (word.length > 20) {
        return (
          <React.Fragment key={index}>
            <span className="break-all">{word}</span>{" "}
          </React.Fragment>
        );
      }

      return (
        <React.Fragment key={index}>
          {word}{" "}
        </React.Fragment>
      );
    });
  };

  return (
  <>
    <div
      className={`mx-auto flex h-full w-full max-w-4xl flex-col gap-3 overflow-y-auto p-3 md:p-4 ${
        messages?.length ? "" : "items-center justify-center"
      }`}
    >
      {messages?.length ? (
        <>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex w-full ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`flex max-w-[85%] flex-col md:max-w-[75%] ${
                  message.role === "user" ? "items-end" : "items-start"
                }`}
              >
                {/* Container for message content or the 'Thinking' loading animation. */}
                <div
                  className={`max-w-full w-fit rounded-2xl px-3 py-2.5 md:py-3 ${
                    message.role === "user"
                      ? "rounded-tr-none bg-red-700 text-white"
                      : "rounded-tl-none bg-gray-200 text-black"
                  }`}
                >
                  <div
                    className={`max-w-full w-fit rounded-2xl px-3 py-2.5 md:py-3 ${
                      message.role === "user"
                        ? "rounded-tr-none bg-red-700 text-white"
                        : "rounded-tl-none bg-gray-200 text-black"
                    }`}
                  >
                    <span className="block max-w-full whitespace-pre-wrap wrap-break-words text-sm md:text-base">
                      {handleChatLength(message.content)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {showThinking && (
            <div className="flex w-full justify-start">
              <div className="w-fit rounded-2xl rounded-tl-none bg-gray-200 px-3 py-2.5 md:py-3">
                <svg
                  className="h-5 w-5 animate-spin text-red-700"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              </div>
            </div>
          )}

          {pending && onResolve && (
            <div className="flex w-full justify-start gap-2 pl-1">
              {(pending.options ?? ["yes", "no"]).map((opt) => (
                <button
                  key={opt}
                  onClick={() => onResolve(opt as "yes" | "no")}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                    opt === "yes"
                      ? "bg-red-700 text-white hover:bg-red-800"
                      : "bg-gray-200 text-black hover:bg-gray-300"
                  }`}
                >
                  {OPTION_LABEL[opt] ?? opt}
                </button>
              ))}
            </div>
          )}
        </>
      ) : (
        <h1 className="flex max-w-full flex-col px-4 text-center text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
          <span className="text-[#870e03] dark:text-[#e7a320]">
            Hello!
          </span>

          <br />

          <span className="mt-2 block text-xl font-medium sm:text-2xl md:text-3xl">
            <TypeAnimation
              sequence={[
                "How can I help you today?",
                3000,
                "Feel free to ask me about store!",
                3000
              ]}
              speed={{
                type: "keyStrokeDelayInMs",
                value: 25,
              }}
              repeat={Infinity}
            />
          </span>
        </h1>
      )}
    </div>
  </>
);
}