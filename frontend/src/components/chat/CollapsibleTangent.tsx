"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChevronDown, GitBranch } from "lucide-react";

interface CollapsibleTangentProps {
  title: string;
  children: string;
  defaultOpen?: boolean;
  onToggle?: () => void;
}

export default function CollapsibleTangent({
  title,
  children,
  defaultOpen = true,
  onToggle,
}: CollapsibleTangentProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentHeight, setContentHeight] = useState<number | undefined>(
    undefined,
  );

  // Measure content height for smooth animation
  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight);
    }
  }, [children]);

  const toggle = () => {
    setIsOpen((prev) => !prev);
    onToggle?.();
  };

  return (
    <div className="tangent-container my-3 animate-fade-in-up">
      {/* Toggle Header */}
      <button
        onClick={toggle}
        className="tangent-toggle group w-full flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all duration-300 hover:bg-[var(--bg-tertiary)]"
      >
        <GitBranch
          size={13}
          className="tangent-icon flex-shrink-0 text-[var(--accent-secondary)] opacity-70"
        />
        <span className="tangent-marker flex-shrink-0 text-[11px] font-mono font-bold text-[var(--accent-secondary)] opacity-80">
          {isOpen ? "[−]" : "[+]"}
        </span>
        <span
          className={`text-xs font-medium transition-colors duration-300 ${
            isOpen
              ? "text-[var(--accent-secondary)]"
              : "text-[var(--text-muted)]"
          }`}
        >
          {isOpen ? title : `Explored: ${title}`}
        </span>
        <ChevronDown
          size={12}
          className={`ml-auto flex-shrink-0 text-[var(--text-muted)] transition-transform duration-300 ${
            isOpen ? "rotate-0" : "-rotate-90"
          }`}
        />
      </button>

      {/* Collapsible Content */}
      <div
        className="tangent-content-wrapper overflow-hidden transition-all duration-400 ease-[cubic-bezier(0.4,0,0.2,1)]"
        style={{
          maxHeight: isOpen
            ? contentHeight
              ? `${contentHeight + 32}px`
              : "2000px"
            : "0px",
          opacity: isOpen ? 1 : 0,
        }}
      >
        <div ref={contentRef} className="tangent-body pl-4 pt-2 pb-1">
          <div className="markdown-content text-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {children}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
