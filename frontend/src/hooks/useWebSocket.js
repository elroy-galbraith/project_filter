/**
 * useWebSocket Hook
 *
 * Manages WebSocket connection for live audio streaming.
 *
 * Features:
 * - Automatic connection management
 * - Event-based message handling
 * - Binary data sending (audio chunks)
 * - Reconnection handling
 * - Connection state tracking
 *
 * Usage:
 *   const { sendAudio, connectionState, lastMessage } = useWebSocket({
 *     url: 'ws://localhost:8000/ws/live',
 *     onMessage: (data) => {
 *       // Handle updates from server
 *       console.log(data.type, data);
 *     }
 *   });
 */

import { useState, useRef, useCallback, useEffect } from 'react';

export const useWebSocket = ({ url, onMessage, onError, autoConnect = false }) => {
  const [connectionState, setConnectionState] = useState('disconnected'); // disconnected, connecting, connected, error
  const [lastMessage, setLastMessage] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    setConnectionState('connecting');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionState('connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          if (onMessage) {
            onMessage(data);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setConnectionState('error');

        if (onError) {
          onError(event);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setConnectionState('disconnected');
        wsRef.current = null;

        // Auto-reconnect after 3 seconds if not closed intentionally
        if (event.code !== 1000 && autoConnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 3000);
        }
      };

    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setConnectionState('error');

      if (onError) {
        onError(err);
      }
    }
  }, [url, onMessage, onError, autoConnect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }

    setConnectionState('disconnected');
  }, []);

  const sendAudio = useCallback((audioBlob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(audioBlob);
    } else {
      console.warn('WebSocket not connected, cannot send audio');
    }
  }, []);

  const sendJSON = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, cannot send data');
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    sendAudio,
    sendJSON,
    connectionState,
    lastMessage,
    isConnected: connectionState === 'connected'
  };
};

export default useWebSocket;
