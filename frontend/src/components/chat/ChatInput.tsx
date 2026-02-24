"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Describe your idea...",
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }, [value]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative glass-panel p-2 flex items-end gap-2">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="
          flex-1 bg-transparent text-[var(--text-primary)] text-sm
          placeholder:text-[var(--text-muted)]
          resize-none outline-none px-3 py-2
          max-h-40 overflow-y-auto
        "
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        className={`
          flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center
          transition-all duration-300
          ${
            disabled || !value.trim()
              ? "bg-[var(--bg-tertiary)] text-[var(--text-muted)] cursor-not-allowed"
              : "gradient-primary text-white hover:shadow-[var(--shadow-glow)] cursor-pointer active:scale-95"
          }
        `}
      >
        {disabled ? (
          <Loader2 size={16} className="animate-spin" />
        ) : (
          <Send size={16} />
        )}
      </button>
    </div>
  );
}
