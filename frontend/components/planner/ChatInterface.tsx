"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiSend, FiUser, FiCpu, FiMic, FiSquare } from "react-icons/fi";
import clsx from "clsx";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatStore } from "@/store/chatStore";

export default function ChatInterface() {
    const {
        messages,
        inputValue,
        isTyping,
        isLoading,
        setInputValue,
        sendMessage,
        loadChatHistory,
        stopStreaming
    } = useChatStore();

    const [isListening, setIsListening] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const recognitionRef = useRef<any>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Load chat history on mount
    useEffect(() => {
        console.log('🎬 [CHAT_INTERFACE] Mounting and loading history...');
        loadChatHistory();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    // Initialize speech recognition
    useEffect(() => {
        if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onresult = (event: any) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }

                if (finalTranscript) {
                    setInputValue(inputValue + finalTranscript);
                }
            };

            recognitionRef.current.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [inputValue, setInputValue]);

    const toggleListening = () => {
        if (!recognitionRef.current) {
            alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        } else {
            recognitionRef.current.start();
            setIsListening(true);
        }
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim() || isTyping) return;

        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        await sendMessage();
    };

    const handleStopGeneration = () => {
        stopStreaming();
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputValue(e.target.value);
    };

    // Auto-resize textarea when input value changes
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [inputValue]);

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
                {messages.length === 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex gap-3 max-w-[85%]"
                    >
                        <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 bg-gray-100 border border-gray-200 text-gray-600">
                            <FiCpu size={14} />
                        </div>

                        <div className="p-4 rounded-2xl text-sm leading-relaxed shadow-sm bg-white text-gray-800 border border-gray-100 rounded-tl-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                "Hello! I'm your **LifePilot Planner**. I create structured plans, routines, and schedules for any area of life where you want improvement. What would you like to plan today?"
                            </ReactMarkdown>
                        </div>
                    </motion.div>
                )}

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
                            {message.role === "assistant" ? (
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        table: ({ node, ...props }) => (
                                            <div className="overflow-x-auto my-4 rounded-lg border border-gray-200">
                                                <table className="w-full border-collapse bg-gray-50" {...props} />
                                            </div>
                                        ),
                                        thead: ({ node, ...props }) => <thead className="bg-gray-100" {...props} />,
                                        th: ({ node, ...props }) => <th className="px-4 py-2 text-left font-semibold text-gray-700 border-b border-gray-200" {...props} />,
                                        td: ({ node, ...props }) => <td className="px-4 py-2 text-gray-600 border-b border-gray-100" {...props} />,
                                        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-4 mb-3 text-gray-900" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-4 mb-2 text-gray-900" {...props} />,
                                        h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mt-3 mb-2 text-gray-800" {...props} />,
                                        ul: ({ node, ...props }) => <ul className="mb-3 space-y-1 list-disc list-inside" {...props} />,
                                        ol: ({ node, ...props }) => <ol className="mb-3 space-y-1 list-decimal list-inside" {...props} />,
                                        li: ({ node, ...props }) => <li className="text-gray-700 ml-2" {...props} />,
                                        p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
                                        strong: ({ node, ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
                                        a: ({ node, ...props }) => (
                                            <a
                                                className="text-primary-600 hover:text-primary-700 underline font-medium transition-colors"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                {...props}
                                            />
                                        ),
                                        code: ({ node, inline, ...props }: any) => {
                                            return inline ? (
                                                <code className="bg-gray-100 rounded px-1.5 py-0.5 text-sm border border-gray-200 text-gray-800" {...props} />
                                            ) : (
                                                <pre className="bg-gray-100 rounded-lg p-3 text-sm overflow-x-auto my-3 border border-gray-200">
                                                    <code className="text-gray-800" {...props} />
                                                </pre>
                                            );
                                        },
                                        hr: ({ node, ...props }) => <hr className="my-4 border-gray-200" {...props} />,
                                    }}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            ) : (
                                message.content
                            )}
                        </div>
                    </motion.div>
                ))}

                {(isTyping || isLoading) && (
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

            {/* Input Area with Voice Button */}
            <div className="p-4 bg-white border-t border-gray-100">
                <div className={clsx(
                    "relative bg-gray-50 border rounded-2xl p-2 transition-all duration-300 focus-within:ring-2 focus-within:ring-primary-100",
                    isListening ? "border-red-400 ring-2 ring-red-100" : "border-gray-200 focus-within:border-primary-300 hover:bg-gray-100/50"
                )}>
                    <div className="flex flex-col gap-2">
                        <textarea
                            ref={textareaRef}
                            value={inputValue}
                            onChange={handleChange}
                            onKeyDown={handleKeyPress}
                            placeholder={isTyping ? "AI is processing..." : isListening ? "Listening..." : "Type your plan here or use voice..."}
                            className="w-full px-2 bg-transparent border-0 focus:outline-none resize-none text-base text-gray-900 placeholder-gray-500"
                            rows={1}
                            style={{ maxHeight: '200px' }}
                            disabled={isTyping || isLoading}
                        />
                        <div className="flex justify-end items-center px-1 gap-2">
                            <button
                                onClick={toggleListening}
                                className={clsx(
                                    "p-2 rounded-xl transition-all duration-200 flex items-center gap-2 text-sm",
                                    isListening
                                        ? "bg-red-100 text-red-600 hover:bg-red-200 animate-pulse"
                                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                                )}
                                title={isListening ? "Stop listening" : "Start voice input"}
                            >
                                <FiMic size={16} />
                                {isListening && <span className="text-xs">Listening...</span>}
                            </button>
                            {(isTyping || isLoading) ? (
                                <button
                                    onClick={handleStopGeneration}
                                    className="p-2 rounded-xl transition-all duration-200 flex items-center justify-center shadow-sm bg-red-500 text-white hover:bg-red-600 hover:scale-105"
                                    title="Stop generating"
                                >
                                    <FiSquare size={18} />
                                </button>
                            ) : (
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!inputValue.trim()}
                                    className={clsx(
                                        "p-2 rounded-xl transition-all duration-200 flex items-center justify-center shadow-sm",
                                        inputValue.trim()
                                            ? "bg-primary-600 text-white hover:bg-primary-700 hover:scale-105"
                                            : "bg-gray-100 text-gray-400 cursor-not-allowed"
                                    )}
                                >
                                    <FiSend size={18} className={clsx(inputValue.trim() && "ml-0.5")} />
                                </button>
                            )}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
