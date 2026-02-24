"use client";

import React, { useState } from "react";
import { GitBranch, Database, ArrowRightLeft, Lock } from "lucide-react";
import type { DiagramType, GraphUpdate } from "@/types/architecture";

interface CanvasPaneProps {
  diagrams: Record<DiagramType, string | null>;
  isFinalized: boolean;
}

const TABS: { key: DiagramType; label: string; icon: React.ReactNode }[] = [
  {
    key: "flowchart",
    label: "Flowchart",
    icon: <GitBranch size={14} />,
  },
  { key: "erd", label: "ERD", icon: <Database size={14} /> },
  {
    key: "sequence",
    label: "Sequence",
    icon: <ArrowRightLeft size={14} />,
  },
];

export default function CanvasPane({ diagrams, isFinalized }: CanvasPaneProps) {
  const [activeTab, setActiveTab] = useState<DiagramType>("flowchart");

  const hasDiagrams = Object.values(diagrams).some(Boolean);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--glass-border)]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg gradient-secondary flex items-center justify-center">
            <GitBranch size={16} className="text-white" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[var(--text-primary)]">
              Architecture Canvas
            </h2>
            <p className="text-[11px] text-[var(--text-muted)]">
              Mermaid.js Diagrams
            </p>
          </div>
        </div>

        {isFinalized && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[hsla(145,70%,50%,0.1)] border border-[hsla(145,70%,50%,0.2)]">
            <Lock size={11} className="text-[var(--accent-success)]" />
            <span className="text-[11px] font-medium text-[var(--accent-success)]">
              Locked
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[var(--glass-border)]">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`
              flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium
              border-b-2 transition-all duration-300 cursor-pointer
              ${
                activeTab === tab.key
                  ? "border-[var(--accent-secondary)] text-[var(--accent-secondary)]"
                  : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }
            `}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Canvas Area */}
      <div className="flex-1 overflow-auto p-6">
        {!hasDiagrams ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 rounded-2xl bg-[var(--bg-tertiary)] flex items-center justify-center mb-4">
              <GitBranch size={32} className="text-[var(--text-muted)]" />
            </div>
            <h3 className="text-base font-semibold text-[var(--text-secondary)] mb-2">
              No Diagrams Yet
            </h3>
            <p className="text-sm text-[var(--text-muted)] max-w-xs">
              Architecture diagrams will appear here once the design discussion
              is finalized.
            </p>
          </div>
        ) : (
          <div className="animate-fade-in">
            {diagrams[activeTab] ? (
              <div className="glass-panel p-6 rounded-xl">
                {/* Phase 2: This will be replaced with actual Mermaid rendering */}
                <pre className="text-xs text-[var(--text-secondary)] font-mono whitespace-pre-wrap overflow-auto">
                  {diagrams[activeTab]}
                </pre>
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 text-sm text-[var(--text-muted)]">
                No {activeTab} diagram generated yet
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
