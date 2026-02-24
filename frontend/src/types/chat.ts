/* ── Chat Types ───────────────────────────────────────────── */

export interface DecisionOption {
  label: string;
  value: string;
  description: string;
}

export interface Decision {
  id: string;
  question: string;
  options: DecisionOption[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata?: {
    decisions?: Decision[];
  };
  createdAt: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  phase: ConversationPhase;
  createdAt: string;
  updatedAt: string;
}

export type ConversationPhase =
  | "negotiation"
  | "architecture"
  | "execution"
  | "evaluation"
  | "deployment";
