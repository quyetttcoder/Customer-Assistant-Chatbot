"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { InterruptPayload, ChatMessage, ServerEvent, ClientEvent } from "../components/type";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export function useChatWebsocket() {
    const wsRef = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [pending, setPending] = useState<InterruptPayload | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [connected, setConnected] = useState<boolean>(false);

    const finishStream = () => setMessages((prev) => {
        const last = prev[prev.length - 1];
        if(last?.role === "assistant" && last.stream) {
            return [...prev.slice(0, -1), {...last, stream:false}];
        };
        return prev
    });

    useEffect(() => {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => setConnected(true);
        ws.onclose = () => {
            if (wsRef.current !== ws) return;
            setConnected(false);
            setLoading(false);
        };

        ws.onmessage = (e) => {
            const ev: ServerEvent = JSON.parse(e.data);
            
            switch (ev.type) {
                case "token":
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last?.role === "assistant" && last.stream) {
                            return [...prev.slice(0, -1), {...last, content: last.content + ev.content}];
                        }
                        return [...prev, {role: "assistant", content: ev.content, stream: true}];
                    });
                    break;
                
                case "interrupt":
                    finishStream();
                    setMessages((prev) => [
                        ...prev,
                        {role: "assistant", content: ev.payload.message}
                    ]);
                    setPending(ev.payload);
                    setLoading(false);
                    break;
                
                case "done":
                    finishStream();
                    setLoading(false);
                    break;

                case "error":
                    console.log("BE error:", ev.message)
                    finishStream();
                    setLoading(false);
                    setMessages((prev) => [...prev, {role: "assistant", content: "Getting an error, please try again!"}])
                    break;
            }
        };

        return () => {
            ws.close();
        };
    }, []);

    const send = useCallback((ev: ClientEvent) => {
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(ev));
            return true;
        };
        console.warn("ws not open, message dropped", ws?.readyState);
        return false;
    }, []);

    const sendMessage = useCallback((content: string) => {
        if (!send({type: "user_message", content})) return;
        setMessages((prev) => [...prev, {role:"user", content}]);
        setLoading(true);
    }, [send]);

    const resolveInterrupt = useCallback((approved: "yes" | "no") => {
        setPending(null);
        setLoading(true);
        send({type: "resume", approved})
    }, [send]);

    return {
        messages,
        pending,
        loading,
        connected,
        sendMessage,
        resolveInterrupt
    }
};
