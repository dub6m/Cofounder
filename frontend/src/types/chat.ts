/* ── Chat Types ───────────────────────────────────────────── */

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
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
