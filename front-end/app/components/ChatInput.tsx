"use client";
import React, { useRef, useState } from "react";
import { IoIosSend } from "react-icons/io";

interface DialogProps {
    disable: boolean;
    onSend: (message: string) => void;
}

export default function ChatInput({ onSend, disable }: DialogProps) {
    const [input, setInput] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const target = e.target;
        setInput(target.value);

        
        target.style.height = "0px";
        target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
    };


    const handleSend = () => {
        if (!input.trim()) return;

        onSend(input);

        setInput("");
        if (textareaRef.current) {
            textareaRef.current.style.height = "0px";
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="
        flex flex-col
        rounded-2xl md:rounded-3xl
        border border-gray-200
        bg-gray-50
        px-3 py-3 md:px-4 md:py-4
        shadow-lg
        dark:border-white/10
        dark:bg-[#2f2f2f]
        dark:shadow-2xl
        w-[75%]
        ">
        <textarea
            name="chat_input"
            id="chat"
            ref={textareaRef}
            value={input}
            onKeyDown={handleKeyDown}
            onChange={handleInputChange}
            rows={1}
            placeholder="Type your question here..."
            disabled={disable}
            className="
            block
            w-full
            px-1 md:px-2
            resize-none
            overflow-y-auto
            bg-transparent
            text-base md:text-lg
            dark:text-white
            placeholder:text-gray-400
            focus:outline-none
            not-dark:caret-black
            min-h-7
            max-h-40 md:max-h-50
            "
        />

        {input.trim() && <div className="flex items-center justify-end mt-2">
            <button 
            onClick={handleSend}
            disabled={disable}
            className="
            flex h-8 w-8 md:h-9 md:w-9 items-center justify-center rounded-full bg-white border border-gray-200 dark:border-none hover:cursor-pointer shadow-sm active:scale-95 transition
            disabled:bg-gray-100 disabled:border-gray-200 dark:disabled:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
            "
            >
            <IoIosSend className="text-black text-lg md:text-xl"/>
            </button>
        </div>}
    </div>
    );
}