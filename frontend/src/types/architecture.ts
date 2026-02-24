/* ── Architecture Types ───────────────────────────────────── */

export type DiagramType = "flowchart" | "erd" | "sequence";

export interface ArchitectureSnapshot {
  id: string;
  conversationId: string;
  version: number;
  flowchart: string | null;
  erd: string | null;
  sequence: string | null;
  isFinalized: boolean;
  createdAt: string;
}

export interface GraphUpdate {
  diagramType: DiagramType;
  mermaidSource: string;
  diff?: string;
}
