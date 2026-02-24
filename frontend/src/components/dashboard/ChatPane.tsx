"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import { MessageSquare, Wifi, WifiOff } from "lucide-react";
import MessageBubble from "@/components/chat/MessageBubble";
import DecisionCard from "@/components/chat/DecisionCard";
import ChatInput from "@/components/chat/ChatInput";
import type { ChatMessage, Decision } from "@/types/chat";

interface ChatPaneProps {
  messages: ChatMessage[];
  onSendMessage: (content: string) => void;
  onDecisionSelect: (decisionId: string, selectedValue: string) => void;
  isConnected: boolean;
  isLoading: boolean;
}

export default function ChatPane({
  messages,
  onSendMessage,
  onDecisionSelect,
  isConnected,
  isLoading,
}: ChatPaneProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  // Map of decisionId -> selectedValue (preserves which option was chosen)
  const [decisions, setDecisions] = useState<Map<string, string>>(new Map());

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
    // Small delay to let the CSS transition start measuring
    setTimeout(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, 350);
  }, []);

  const handleDecision = (decisionId: string, selectedValue: string) => {
    setDecisions((prev) => {
      const next = new Map(prev);
      next.set(decisionId, selectedValue);
      return next;
    });
    onDecisionSelect(decisionId, selectedValue);
  };

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
              Your Thought Partner
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
          <React.Fragment key={msg.id}>
            <MessageBubble
              message={msg}
              onDeepDiveToggle={handleDeepDiveToggle}
            />

            {/* Render Decision Cards inline after the assistant message */}
            {msg.role === "assistant" &&
              msg.metadata?.decisions?.map((decision: Decision) => (
                <div key={decision.id} className="ml-11">
                  <DecisionCard
                    decision={decision}
                    onSelect={handleDecision}
                    selectedValue={decisions.get(decision.id) ?? null}
                  />
                </div>
              ))}
          </React.Fragment>
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
