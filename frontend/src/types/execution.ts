/* ── Execution Types ──────────────────────────────────────── */

export type StepStatus = "pending" | "running" | "passed" | "failed";

export interface ExecutionStep {
  index: number;
  label: string;
  status: StepStatus;
}

export interface TestResult {
  exitCode: number;
  summary: string;
  stderrTail?: string;
}

export interface ScoutAlert {
  severity: "low" | "blocker";
  issueDescription: string;
  suggestedArchitecture?: string;
}
