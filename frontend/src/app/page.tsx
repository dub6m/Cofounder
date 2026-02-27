"use client";

import React, { useState, useCallback } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import ChatPane from "@/components/dashboard/ChatPane";
import CanvasPane from "@/components/dashboard/CanvasPane";
import RealityPane from "@/components/dashboard/RealityPane";
import type { ChatMessage } from "@/types/chat";
import type { DiagramType } from "@/types/architecture";
import type { ExecutionStep, TestResult } from "@/types/execution";
import type { EventType } from "@/lib/wsEvents";
import { Layers, Sparkles } from "lucide-react";

export default function DashboardPage() {
  // ── State ──────────────────────────────────────────────────
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [phase, setPhase] = useState<string>("negotiation");
  const [isLoading, setIsLoading] = useState(false);
  const [diagrams, setDiagrams] = useState<Record<DiagramType, string | null>>({
    flowchart: null,
    erd: null,
    sequence: null,
  });
  const [isFinalized, setIsFinalized] = useState(false);
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [testResult, setTestResult] = useState<TestResult | null>(null);

  // ── WebSocket Event Handler ────────────────────────────────
  const handleWsEvent = useCallback(
    (eventType: EventType, payload: Record<string, unknown>) => {
      switch (eventType) {
        case "chat_message": {
          const msg: ChatMessage = {
            id: crypto.randomUUID(),
            role: payload.role as "user" | "assistant" | "system",
            content: payload.content as string,
            metadata: payload.metadata as ChatMessage["metadata"],
            createdAt: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, msg]);
          setIsLoading(false);
          break;
        }

        case "phase_change": {
          const toPhase = payload.to_phase as string;
          setPhase(toPhase);

          // Capture conversation ID from initial phase change
          if (payload.conversation_id) {
            setConversationId(payload.conversation_id as string);
          }

          if (toPhase === "architecture") {
            setIsFinalized(true);
          }
          break;
        }

        case "graph_update": {
          const diagramType = payload.diagram_type as DiagramType;
          const mermaidSource = payload.mermaid_source as string;
          setDiagrams((prev) => ({
            ...prev,
            [diagramType]: mermaidSource,
          }));
          break;
        }

        case "execution_progress": {
          const step: ExecutionStep = {
            index: payload.step_index as number,
            label: payload.step_label as string,
            status: payload.status as ExecutionStep["status"],
          };
          setExecutionSteps((prev) => {
            const updated = [...prev];
            const existing = updated.findIndex((s) => s.index === step.index);
            if (existing >= 0) {
              updated[existing] = step;
            } else {
              updated.push(step);
            }
            return updated.sort((a, b) => a.index - b.index);
          });
          break;
        }

        case "test_result": {
          setTestResult({
            exitCode: payload.exit_code as number,
            summary: payload.summary as string,
            stderrTail: payload.stderr_tail as string | undefined,
          });
          break;
        }

        case "scout_alert": {
          // Display scout alerts as system messages in chat
          const alertMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: "system",
            content: `⚠️ **Scout Alert (${payload.severity}):** ${payload.issue_description}`,
            createdAt: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, alertMsg]);
          break;
        }

        case "error": {
          console.error("[Backend Error]", payload.message);
          setIsLoading(false);
          break;
        }
      }
    },
    [],
  );

  const { isConnected, sendEvent } = useWebSocket({
    onEvent: handleWsEvent,
  });

  // ── Handlers ───────────────────────────────────────────────
  const handleSendMessage = useCallback(
    (content: string) => {
      // Add user message to local state immediately
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      // Send to backend
      sendEvent("user_message", {
        content,
        conversation_id: conversationId,
      });
    },
    [sendEvent, conversationId],
  );

  // ── Render ─────────────────────────────────────────────────
  return (
    <div className="h-screen flex flex-col bg-[var(--bg-primary)]">
      {/* Top Bar */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-[var(--glass-border)] bg-[var(--bg-secondary)]/50 backdrop-blur-lg">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-[var(--shadow-glow)]">
            <Layers size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold gradient-text">Cofounder</h1>
            <p className="text-[10px] text-[var(--text-muted)] -mt-0.5">
              AI Codebase Orchestrator
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Phase indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass-panel">
            <Sparkles size={12} className="text-[var(--accent-primary)]" />
            <span className="text-[11px] font-medium text-[var(--text-secondary)] capitalize">
              {phase.replace("_", " ")}
            </span>
          </div>
        </div>
      </header>

      {/* 3-Pane Dashboard */}
      <main className="flex-1 flex gap-3 p-3 min-h-0">
        {/* Pane 1: Chat (Left) */}
        <section className="w-[380px] flex-shrink-0 glass-panel overflow-hidden flex flex-col">
          <ChatPane
            messages={messages}
            onSendMessage={handleSendMessage}
            isConnected={isConnected}
            isLoading={isLoading}
          />
        </section>

        {/* Pane 2: Canvas (Center) */}
        <section className="flex-1 glass-panel overflow-hidden flex flex-col min-w-0">
          <CanvasPane diagrams={diagrams} isFinalized={isFinalized} />
        </section>

        {/* Pane 3: Reality Engine (Right) */}
        <section className="w-[300px] flex-shrink-0 glass-panel overflow-hidden flex flex-col">
          <RealityPane
            steps={executionSteps}
            logs={logs}
            testResult={testResult}
            phase={phase}
          />
        </section>
      </main>
    </div>
  );
}
