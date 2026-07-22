"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: unknown) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "reconnecting";

export function useWebSocket({
  url,
  onMessage,
  reconnectInterval = 2000,
  maxReconnectAttempts = 10,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const wsRef = useRef<WebSocket | null>(null);
  const attemptsRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    setStatus("connecting");
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus("connected");
      attemptsRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch {
        onMessage?.(event.data);
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
      wsRef.current = null;

      if (attemptsRef.current < maxReconnectAttempts) {
        const delay = reconnectInterval * Math.pow(2, attemptsRef.current);
        const capped = Math.min(delay, 30000);
        setStatus("reconnecting");
        reconnectTimerRef.current = setTimeout(() => {
          attemptsRef.current++;
          connect();
        }, capped);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [url, onMessage, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    attemptsRef.current = maxReconnectAttempts;
    wsRef.current?.close();
  }, [maxReconnectAttempts]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  return { status, send, disconnect };
}
