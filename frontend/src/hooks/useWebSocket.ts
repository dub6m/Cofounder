"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createEvent, type EventType, type WsEnvelope } from "@/lib/wsEvents";

interface UseWebSocketOptions {
  url?: string;
  onEvent?: (eventType: EventType, payload: Record<string, unknown>) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  sendEvent: (eventType: EventType, payload: Record<string, unknown>) => void;
  lastEvent: WsEnvelope | null;
}

export function useWebSocket({
  url = "ws://localhost:8000/ws",
  onEvent,
  reconnectInterval = 3000,
  maxReconnectAttempts = 10,
}: UseWebSocketOptions = {}): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<WsEnvelope | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(
    undefined,
  );
  const onEventRef = useRef(onEvent);

  // Keep the callback ref current
  onEventRef.current = onEvent;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
        console.log("[WS] Connected to", url);
      };

      ws.onmessage = (event) => {
        try {
          const envelope: WsEnvelope = JSON.parse(event.data);
          setLastEvent(envelope);
          onEventRef.current?.(envelope.event_type, envelope.payload);
        } catch (err) {
          console.error("[WS] Failed to parse message:", err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        console.log("[WS] Disconnected");

        // Auto-reconnect with exponential backoff
        if (reconnectCountRef.current < maxReconnectAttempts) {
          const delay =
            reconnectInterval * Math.pow(1.5, reconnectCountRef.current);
          reconnectCountRef.current++;
          console.log(
            `[WS] Reconnecting in ${Math.round(delay)}ms (attempt ${reconnectCountRef.current})`,
          );
          reconnectTimerRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = (err) => {
        console.error("[WS] Error:", err);
      };

      wsRef.current = ws;
    } catch (err) {
      console.error("[WS] Connection failed:", err);
    }
  }, [url, reconnectInterval, maxReconnectAttempts]);

  const sendEvent = useCallback(
    (eventType: EventType, payload: Record<string, unknown>) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(createEvent(eventType, payload));
      } else {
        console.warn("[WS] Cannot send — not connected");
      }
    },
    [],
  );

  useEffect(() => {
    connect();

    return () => {
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { isConnected, sendEvent, lastEvent };
}
