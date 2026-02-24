/* ── WebSocket Event Types ────────────────────────────────── */

export type EventType =
  | "chat_message"
  | "decision_required"
  | "decision_response"
  | "graph_update"
  | "execution_progress"
  | "test_result"
  | "scout_alert"
  | "deployment_success"
  | "user_message"
  | "phase_change"
  | "error";

export interface WsEnvelope {
  event_type: EventType;
  timestamp: string;
  payload: Record<string, unknown>;
}

/**
 * Create a typed WebSocket event envelope.
 */
export function createEvent(
  eventType: EventType,
  payload: Record<string, unknown>,
): string {
  const envelope: WsEnvelope = {
    event_type: eventType,
    timestamp: new Date().toISOString(),
    payload,
  };
  return JSON.stringify(envelope);
}
