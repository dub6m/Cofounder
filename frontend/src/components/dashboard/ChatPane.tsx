"use client";

import React, { useRef, useEffect, useCallback } from "react";
import { MessageSquare, Wifi, WifiOff } from "lucide-react";
import MessageBubble from "@/components/chat/MessageBubble";
import ChatInput from "@/components/chat/ChatInput";
import type { ChatMessage } from "@/types/chat";

interface ChatPaneProps {
  messages: ChatMessage[];
  onSendMessage: (content: string) => void;
  isConnected: boolean;
  isLoading: boolean;
}

export default function ChatPane({
  messages,
  onSendMessage,
  isConnected,
  isLoading,
}: ChatPaneProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Smooth-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  // Re-adjust scroll when a DeepDive tangent is collapsed/expanded
  const handleDeepDiveToggle = useCallback(() => {
    setTimeout(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, 350);
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--glass-border)]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
            <MessageSquare size={16} className="text-white" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[var(--text-primary)]">
              Cofounder
            </h2>
            <p className="text-[11px] text-[var(--text-muted)]">
              Your Technical Lead
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          {isConnected ? (
            <Wifi size={14} className="text-[var(--accent-success)]" />
          ) : (
            <WifiOff size={14} className="text-[var(--accent-danger)]" />
          )}
          <span
            className={`text-[11px] ${
              isConnected
                ? "text-[var(--accent-success)]"
                : "text-[var(--accent-danger)]"
            }`}
          >
            {isConnected ? "Live" : "Reconnecting..."}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scroll-smooth"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-6">
            <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mb-4 animate-pulse-glow">
              <MessageSquare size={28} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold gradient-text mb-2">
              What are we building?
            </h3>
            <p className="text-sm text-[var(--text-secondary)] max-w-xs leading-relaxed">
              Describe your idea — even a rough sketch is fine. I&apos;ll help
              you sharpen it into something we can actually build.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onDeepDiveToggle={handleDeepDiveToggle}
          />
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex gap-3 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--accent-secondary-dim)] flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-[var(--accent-secondary)] animate-pulse" />
            </div>
            <div className="glass-panel rounded-2xl rounded-tl-md px-4 py-3 max-w-[60%]">
              <div className="flex gap-1.5 items-center">
                <div
                  className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <div
                  className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
                <span className="text-[11px] text-[var(--text-muted)] ml-2">
                  thinking...
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 pt-2">
        <ChatInput
          onSend={onSendMessage}
          disabled={!isConnected || isLoading}
          placeholder={
            !isConnected ? "Reconnecting..." : "Describe your idea..."
          }
        />
      </div>
    </div>
  );
}
