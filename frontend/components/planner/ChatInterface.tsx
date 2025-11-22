"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiSend, FiUser, FiCpu } from "react-icons/fi";
import clsx from "clsx";

type Message = {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
};

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "assistant",
            content: "Hello Jay! I'm ready to help you plan your day. What's on your mind?",
            timestamp: new Date(),
        },
    ]);
    const [inputValue, setInputValue] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const newMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: inputValue,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, newMessage]);
        setInputValue("");
        setIsTyping(true);

        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        // Simulate AI response
        setTimeout(() => {
            setIsTyping(false);
            setMessages((prev) => [
                ...prev,
                {
                    id: (Date.now() + 1).toString(),
                    role: "assistant",
                    content: "I'm processing that for you. I'll update your schedule and tasks accordingly.",
                    timestamp: new Date(),
                },
            ]);
        }, 2000);
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputValue(e.target.value);
        // Auto-resize textarea
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-2xl shadow-soft border border-gray-100 overflow-hidden">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-white z-10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary-50 flex items-center justify-center text-primary-600">
                        <FiCpu size={20} />
                    </div>
                    <div>
                        <h2 className="font-bold text-gray-900">LifePilot Planner</h2>
                        <div className="flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-xs text-gray-500 font-medium">Online</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50/30">
                {messages.map((message) => (
                    <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={clsx(
                            "flex gap-3 max-w-[85%]",
                            message.role === "user" ? "ml-auto flex-row-reverse" : ""
                        )}
                    >
                        <div className={clsx(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                            message.role === "user" ? "bg-primary-100 text-primary-600" : "bg-gray-100 border border-gray-200 text-gray-600"
                        )}>
                            {message.role === "user" ? <FiUser size={14} /> : <FiCpu size={14} />}
                        </div>

                        <div className={clsx(
                            "p-4 rounded-2xl text-sm leading-relaxed shadow-sm",
                            message.role === "user"
                                ? "bg-primary-600 text-white rounded-tr-none"
                                : "bg-white text-gray-800 border border-gray-100 rounded-tl-none"
                        )}>
                            {message.content}
                        </div>
                    </motion.div>
                ))}

                {isTyping && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex gap-3 max-w-[85%]"
                    >
                        <div className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center shrink-0 mt-1 text-gray-600">
                            <FiCpu size={14} />
                        </div>
                        <div className="bg-white border border-gray-100 p-4 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-1">
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area (Old Design Layout) */}
            <div className="p-4 bg-white border-t border-gray-100">
                <div className="relative bg-gray-50 border border-gray-200 rounded-2xl p-2 transition-all duration-300 focus-within:ring-2 focus-within:ring-primary-100 focus-within:border-primary-300 hover:bg-gray-100/50">
                    <div className="flex flex-col gap-2">
                        <textarea
                            ref={textareaRef}
                            value={inputValue}
                            onChange={handleChange}
                            onKeyDown={handleKeyPress}
                            placeholder={isTyping ? "AI is processing..." : "Type your plan here..."}
                            className="w-full px-2 bg-transparent border-0 focus:outline-none resize-none text-base text-gray-900 placeholder-gray-500"
                            rows={1}
                            style={{ maxHeight: '200px' }}
                        />
                        <div className="flex justify-between items-center px-1">
                            <div className="text-xs text-gray-500">
                                {/* Optional: Add icons or hints here like in the old design */}
                            </div>
                            <button
                                onClick={handleSendMessage}
                                disabled={!inputValue.trim() || isTyping}
                                className={clsx(
                                    "p-2 rounded-xl transition-all duration-200 flex items-center justify-center shadow-sm",
                                    inputValue.trim() && !isTyping
                                        ? "bg-primary-600 text-white hover:bg-primary-700 hover:scale-105"
                                        : "bg-gray-100 text-gray-400 cursor-not-allowed"
                                )}
                            >
                                <FiSend size={18} className={clsx(inputValue.trim() && !isTyping && "ml-0.5")} />
                            </button>
                        </div>
                    </div>
                </div>
                <p className="text-center text-xs text-gray-400 mt-2">
                    Press Enter to send • AI can make mistakes, please verify.
                </p>
            </div>
        </div>
    );
}
