"use client";

import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "@/types/chat";
import { Bot, User, AlertTriangle } from "lucide-react";
import CollapsibleTangent from "./CollapsibleTangent";

interface MessageBubbleProps {
  message: ChatMessage;
  onDeepDiveToggle?: () => void;
}

// ── DeepDive Tag Parser ────────────────────────────────────────

interface ContentSegment {
  type: "markdown" | "deepdive";
  content: string;
  title?: string;
}

const DEEP_DIVE_REGEX =
  /<DeepDive\s+title="([^"]*)">\s*([\s\S]*?)\s*<\/DeepDive>/g;

function parseContent(raw: string): ContentSegment[] {
  const segments: ContentSegment[] = [];
  let lastIndex = 0;

  for (const match of raw.matchAll(DEEP_DIVE_REGEX)) {
    const matchStart = match.index!;

    // Push any markdown before this DeepDive
    if (matchStart > lastIndex) {
      const before = raw.slice(lastIndex, matchStart).trim();
      if (before) {
        segments.push({ type: "markdown", content: before });
      }
    }

    // Push the DeepDive
    segments.push({
      type: "deepdive",
      title: match[1],
      content: match[2].trim(),
    });

    lastIndex = matchStart + match[0].length;
  }

  // Push any remaining markdown after the last DeepDive
  if (lastIndex < raw.length) {
    const remaining = raw.slice(lastIndex).trim();
    if (remaining) {
      segments.push({ type: "markdown", content: remaining });
    }
  }

  // If no DeepDives found, return the whole thing as markdown
  if (segments.length === 0) {
    segments.push({ type: "markdown", content: raw });
  }

  return segments;
}

// ── Component ──────────────────────────────────────────────────

export default function MessageBubble({
  message,
  onDeepDiveToggle,
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  const segments = useMemo(
    () => (isUser || isSystem ? null : parseContent(message.content)),
    [message.content, isUser, isSystem],
  );

  // System messages (scout alerts, etc.)
  if (isSystem) {
    return (
      <div className="flex gap-3 animate-fade-in-up px-2">
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-[hsla(35,100%,60%,0.15)] flex items-center justify-center">
          <AlertTriangle size={13} className="text-[var(--accent-warning)]" />
        </div>
        <div className="glass-panel rounded-2xl px-4 py-2.5 max-w-[90%] border-l-2 border-[var(--accent-warning)]">
          <div className="markdown-content text-xs">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex gap-3 animate-fade-in-up ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? "bg-[var(--accent-primary-dim)] text-[var(--accent-primary)]"
            : "bg-[var(--accent-secondary-dim)] text-[var(--accent-secondary)]"
        }`}
      >
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-[var(--accent-primary)] text-white rounded-tr-md"
            : "glass-panel rounded-tl-md"
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed">{message.content}</p>
        ) : (
          <div className="text-sm">
            {segments!.map((seg, i) =>
              seg.type === "deepdive" ? (
                <CollapsibleTangent
                  key={i}
                  title={seg.title!}
                  onToggle={onDeepDiveToggle}
                >
                  {seg.content}
                </CollapsibleTangent>
              ) : (
                <div key={i} className="markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {seg.content}
                  </ReactMarkdown>
                </div>
              ),
            )}
          </div>
        )}
      </div>
    </div>
  );
}
