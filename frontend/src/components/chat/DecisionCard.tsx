"use client";

import React from "react";
import type { Decision, DecisionOption } from "@/types/chat";
import { Sparkles, Check } from "lucide-react";

interface DecisionCardProps {
  decision: Decision;
  onSelect: (decisionId: string, selectedValue: string) => void;
  selectedValue?: string | null;
}

export default function DecisionCard({
  decision,
  onSelect,
  selectedValue = null,
}: DecisionCardProps) {
  const isDecided = selectedValue !== null;

  return (
    <div className="decision-card animate-fade-in-up my-4">
      {/* Question Header */}
      <div className="flex items-center gap-2 mb-3">
        <Sparkles
          size={14}
          className="text-[var(--accent-warning)] opacity-80"
        />
        <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--accent-warning)] opacity-80">
          Your Call
        </span>
      </div>
      <p className="text-[13px] font-medium text-[var(--text-primary)] mb-3 leading-relaxed">
        {decision.question}
      </p>

      {/* Options */}
      <div className="flex flex-col gap-2">
        {decision.options.map((option: DecisionOption, idx: number) => {
          const isSelected = selectedValue === option.value;
          const isDimmed = isDecided && !isSelected;

          return (
            <button
              key={option.value}
              onClick={() => {
                if (!isDecided) onSelect(decision.id, option.value);
              }}
              className={`
                decision-option group relative w-full text-left rounded-xl
                overflow-hidden
                transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]
                ${
                  isSelected
                    ? "decision-option--selected"
                    : isDimmed
                      ? "decision-option--dimmed"
                      : "decision-option--available"
                }
              `}
            >
              <div className="flex items-start gap-3 p-3.5">
                {/* Indicator */}
                <div
                  className={`
                    flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center
                    transition-all duration-500
                    ${
                      isSelected
                        ? "bg-[var(--accent-success)] scale-100"
                        : isDimmed
                          ? "bg-[var(--bg-tertiary)] scale-90 opacity-40"
                          : idx === 0
                            ? "bg-[var(--accent-primary-dim)] group-hover:bg-[var(--accent-primary)] group-hover:scale-110"
                            : "bg-[var(--accent-secondary-dim)] group-hover:bg-[var(--accent-secondary)] group-hover:scale-110"
                    }
                  `}
                >
                  {isSelected ? (
                    <Check size={13} className="text-white" />
                  ) : (
                    <span
                      className={`text-[10px] font-bold transition-colors duration-300 ${
                        isDimmed
                          ? "text-[var(--text-muted)]"
                          : idx === 0
                            ? "text-[var(--accent-primary)] group-hover:text-white"
                            : "text-[var(--accent-secondary)] group-hover:text-white"
                      }`}
                    >
                      {String.fromCharCode(65 + idx)}
                    </span>
                  )}
                </div>

                {/* Text */}
                <div className="flex-1 min-w-0 overflow-hidden">
                  <span
                    className={`text-[13px] font-semibold block break-words overflow-wrap-anywhere transition-colors duration-300 ${
                      isSelected
                        ? "text-[var(--accent-success)]"
                        : isDimmed
                          ? "text-[var(--text-muted)]"
                          : "text-[var(--text-primary)]"
                    }`}
                  >
                    {option.label}
                    {isSelected && (
                      <span className="ml-2 text-[10px] font-normal opacity-60">
                        — chosen
                      </span>
                    )}
                  </span>
                  <p
                    className={`text-xs leading-relaxed mt-0.5 break-words overflow-wrap-anywhere transition-all duration-500 ${
                      isSelected
                        ? "text-[var(--text-secondary)]"
                        : isDimmed
                          ? "text-[var(--text-muted)] max-h-0 overflow-hidden opacity-0"
                          : "text-[var(--text-secondary)]"
                    }`}
                  >
                    {option.description}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
