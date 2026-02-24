"use client";

import React, { useState } from "react";
import {
  Activity,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Loader2,
  Circle,
  Terminal,
} from "lucide-react";
import type { ExecutionStep, TestResult } from "@/types/execution";

interface RealityPaneProps {
  steps: ExecutionStep[];
  logs: string[];
  testResult: TestResult | null;
  phase: string;
}

const PHASE_LABELS: Record<string, string> = {
  negotiation: "Design Discussion",
  architecture: "Architecture Locked",
  execution: "Building in Sandbox",
  evaluation: "Evaluating Results",
  deployment: "Deploying to GitHub",
};

function StepStatusIcon({ status }: { status: string }) {
  switch (status) {
    case "passed":
      return (
        <CheckCircle2 size={16} className="text-[var(--accent-success)]" />
      );
    case "failed":
      return <XCircle size={16} className="text-[var(--accent-danger)]" />;
    case "running":
      return (
        <Loader2
          size={16}
          className="text-[var(--accent-primary)] animate-spin"
        />
      );
    default:
      return <Circle size={16} className="text-[var(--text-muted)]" />;
  }
}

export default function RealityPane({
  steps,
  logs,
  testResult,
  phase,
}: RealityPaneProps) {
  const [logsExpanded, setLogsExpanded] = useState(false);

  const defaultSteps: ExecutionStep[] =
    steps.length > 0
      ? steps
      : [
          { index: 0, label: "DB Models", status: "pending" },
          { index: 1, label: "Core Logic", status: "pending" },
          { index: 2, label: "API Layer", status: "pending" },
          { index: 3, label: "Tests", status: "pending" },
        ];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--glass-border)]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center">
            <Activity size={16} className="text-[var(--accent-warning)]" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[var(--text-primary)]">
              Reality Engine
            </h2>
            <p className="text-[11px] text-[var(--text-muted)]">
              {PHASE_LABELS[phase] || phase}
            </p>
          </div>
        </div>
      </div>

      {/* Progress Stepper */}
      <div className="px-5 py-4 space-y-1">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] mb-3">
          Execution Pipeline
        </h3>
        {defaultSteps.map((step, idx) => (
          <div key={step.index} className="flex items-center gap-3 py-2">
            <div className="relative flex flex-col items-center">
              <StepStatusIcon status={step.status} />
              {idx < defaultSteps.length - 1 && (
                <div
                  className={`w-0.5 h-6 mt-1 ${
                    step.status === "passed"
                      ? "bg-[var(--accent-success)]"
                      : "bg-[var(--glass-border)]"
                  }`}
                />
              )}
            </div>
            <span
              className={`text-sm ${
                step.status === "running"
                  ? "text-[var(--accent-primary)] font-medium"
                  : step.status === "passed"
                    ? "text-[var(--accent-success)]"
                    : step.status === "failed"
                      ? "text-[var(--accent-danger)]"
                      : "text-[var(--text-muted)]"
              }`}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>

      {/* Test Result */}
      {testResult && (
        <div className="mx-5 mb-4 p-3 rounded-xl border border-[var(--glass-border)] bg-[var(--bg-secondary)]">
          <div className="flex items-center gap-2 mb-1">
            {testResult.exitCode === 0 ? (
              <CheckCircle2
                size={14}
                className="text-[var(--accent-success)]"
              />
            ) : (
              <XCircle size={14} className="text-[var(--accent-danger)]" />
            )}
            <span className="text-xs font-medium">
              Exit Code: {testResult.exitCode}
            </span>
          </div>
          <p className="text-xs text-[var(--text-secondary)]">
            {testResult.summary}
          </p>
        </div>
      )}

      {/* Expandable Logs */}
      <div className="flex-1 flex flex-col px-5 pb-4 min-h-0">
        <button
          onClick={() => setLogsExpanded(!logsExpanded)}
          className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors cursor-pointer mb-2"
        >
          <Terminal size={12} />
          <span>Terminal Output</span>
          {logsExpanded ? (
            <ChevronDown size={12} />
          ) : (
            <ChevronRight size={12} />
          )}
        </button>

        {logsExpanded && (
          <div className="flex-1 min-h-0 overflow-auto animate-fade-in">
            <div className="bg-[var(--bg-primary)] rounded-lg border border-[var(--glass-border)] p-3 font-mono text-[11px] text-[var(--text-secondary)] max-h-64 overflow-auto">
              {logs.length > 0 ? (
                logs.map((line, i) => (
                  <div
                    key={i}
                    className="leading-5 hover:bg-[var(--bg-tertiary)] px-1 rounded"
                  >
                    <span className="text-[var(--text-muted)] mr-2 select-none">
                      {String(i + 1).padStart(3, " ")}
                    </span>
                    {line}
                  </div>
                ))
              ) : (
                <span className="text-[var(--text-muted)]">
                  No logs yet. Logs will appear here during execution.
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
