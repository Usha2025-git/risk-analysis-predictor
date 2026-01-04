import { useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage } from '../types';

type MessageHandler = (data: WebSocketMessage['data']) => void;

export const useWebSocket = (url: string, clientId: string) => {
  const wsRef = useRef<WebSocket | null>(null);
  const subscribedEventsRef = useRef<Set<string>>(new Set());
  const messageHandlersRef = useRef<Map<string, MessageHandler>>(new Map());

  const subscribe = useCallback((eventType: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'subscribe',
        event_type: eventType,
        client_id: clientId,
      };
      wsRef.current.send(JSON.stringify(message));
      subscribedEventsRef.current.add(eventType);
    }
  }, [clientId]);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = url || `${protocol}//${window.location.host}/api/v1/ws/${clientId}`;
      
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        // Resubscribe to all events
        subscribedEventsRef.current.forEach((eventType) => {
          subscribe(eventType);
        });
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const handler = messageHandlersRef.current.get(message.event_type);
          if (handler) {
            handler(message.data);
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          connect();
        }, 3000);
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }, [clientId, url, subscribe]);

  const unsubscribe = useCallback((eventType: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'unsubscribe',
        event_type: eventType,
        client_id: clientId,
      };
      wsRef.current.send(JSON.stringify(message));
      subscribedEventsRef.current.delete(eventType);
    }
  }, [clientId]);

  const onMessage = useCallback((eventType: string, handler: MessageHandler) => {
    messageHandlersRef.current.set(eventType, handler);
    subscribe(eventType);
  }, [subscribe]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    subscribe,
    unsubscribe,
    onMessage,
    disconnect,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
};
