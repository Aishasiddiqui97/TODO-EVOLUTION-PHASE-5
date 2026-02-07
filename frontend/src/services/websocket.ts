/**
 * WebSocket client for real-time task synchronization.
 *
 * Connects to the WebSocket Sync service and handles real-time task updates.
 */

export interface WebSocketMessage {
  type: string;
  event?: string;
  data?: any;
  sequence?: number;
  timestamp?: string;
  taskId?: string;
  changes?: any;
}

export interface ConnectionStatus {
  connected: boolean;
  currentSequence: number;
  reconnecting: boolean;
  error?: string;
}

export type MessageHandler = (message: WebSocketMessage) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private userId: string;
  private lastSequence: number = 0;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private reconnectDelay: number = 1000; // Start with 1 second
  private maxReconnectDelay: number = 30000; // Max 30 seconds
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private connectionStatus: ConnectionStatus = {
    connected: false,
    currentSequence: 0,
    reconnecting: false
  };
  private statusChangeCallbacks: Set<(status: ConnectionStatus) => void> = new Set();

  constructor(userId: string, wsUrl?: string) {
    this.userId = userId;
    this.wsUrl = wsUrl || this.getDefaultWsUrl();
  }

  private wsUrl: string;

  private getDefaultWsUrl(): string {
    // Determine WebSocket URL based on environment
    // Next.js uses NEXT_PUBLIC_ prefix for client-side env vars
    const envUrl = process.env.NEXT_PUBLIC_WS_URL;
    if (envUrl) {
      return envUrl;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    // Fallback to 8004 if not specified
    const port = process.env.NEXT_PUBLIC_WS_PORT || '8004';
    return `${protocol}//${host}:${port}/ws`;
  }

  /**
   * Connect to WebSocket server.
   */
  public connect(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      const url = `${this.wsUrl}?userId=${encodeURIComponent(this.userId)}&lastSequence=${this.lastSequence}`;
      console.log(`[WebSocket] Attempting to connect to: ${url}`);

      this.ws = new WebSocket(url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);

    } catch (error) {
      console.error('[WebSocket] Error creating connection:', error);
      console.warn('[WebSocket] Make sure the WebSocket service is running. Run: start-websocket-fixed.bat');
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server.
   */
  public disconnect(): void {
    console.log('Disconnecting WebSocket');

    // Clear timers
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }

    // Close connection
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.updateConnectionStatus({ connected: false, reconnecting: false });
  }

  /**
   * Send a message to the server.
   */
  public send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  /**
   * Request full sync from server.
   */
  public requestSync(): void {
    this.send({
      type: 'sync.request',
      lastSequence: this.lastSequence
    });
  }

  /**
   * Check sequence status with server.
   */
  public checkSequence(): void {
    this.send({
      type: 'sequence.check',
      sequence: this.lastSequence
    });
  }

  /**
   * Register a message handler for a specific event type.
   */
  public on(eventType: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(eventType)) {
      this.messageHandlers.set(eventType, new Set());
    }
    this.messageHandlers.get(eventType)!.add(handler);
  }

  /**
   * Unregister a message handler.
   */
  public off(eventType: string, handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * Register a connection status change callback.
   */
  public onStatusChange(callback: (status: ConnectionStatus) => void): void {
    this.statusChangeCallbacks.add(callback);
  }

  /**
   * Unregister a connection status change callback.
   */
  public offStatusChange(callback: (status: ConnectionStatus) => void): void {
    this.statusChangeCallbacks.delete(callback);
  }

  /**
   * Get current connection status.
   */
  public getStatus(): ConnectionStatus {
    return { ...this.connectionStatus };
  }

  private handleOpen(): void {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;

    this.updateConnectionStatus({ connected: true, reconnecting: false });

    // Start ping interval
    this.startPingInterval();
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('WebSocket message received:', message.type);

      // Update sequence number if present
      if (message.sequence !== undefined) {
        this.lastSequence = message.sequence;
        this.updateConnectionStatus({ currentSequence: message.sequence });
      }

      // Handle connection established message
      if (message.type === 'connection.established') {
        const data = message.data || {};
        this.lastSequence = data.currentSequence || 0;
        this.updateConnectionStatus({ currentSequence: this.lastSequence });
      }

      // Dispatch to registered handlers
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error(`Error in message handler for ${message.type}:`, error);
          }
        });
      }

      // Also dispatch to wildcard handlers
      const wildcardHandlers = this.messageHandlers.get('*');
      if (wildcardHandlers) {
        wildcardHandlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error('Error in wildcard message handler:', error);
          }
        });
      }

    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleError(event: Event): void {
    const wsState = this.ws ? ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][this.ws.readyState] : 'NULL';
    
    // Only log detailed errors in development, and make them more informative
    if (process.env.NODE_ENV === 'development') {
      console.warn('WebSocket connection error:', {
        url: this.wsUrl,
        readyState: wsState,
        message: 'Unable to connect to WebSocket server. Make sure the WebSocket service is running on port 8004.',
        hint: 'Run: start-websocket-fixed.bat'
      });
    }
    
    this.updateConnectionStatus({
      connected: false,
      error: 'Connection error - WebSocket service may not be running'
    });
  }

  private handleClose(event: CloseEvent): void {
    const closeReasons: Record<number, string> = {
      1000: 'Normal closure',
      1001: 'Going away',
      1006: 'Connection lost (service may not be running)',
      1011: 'Server error',
      1012: 'Service restart',
      1013: 'Try again later',
      1014: 'Bad gateway',
      1015: 'TLS handshake failed'
    };

    const reason = closeReasons[event.code] || event.reason || 'Unknown reason';
    console.log(`[WebSocket] Connection closed: ${reason} (code: ${event.code})`);

    if (event.code === 1006) {
      console.warn('[WebSocket] 💡 Tip: The WebSocket service may not be running. Run: start-websocket-fixed.bat');
    }

    this.updateConnectionStatus({ connected: false });

    // Clear ping interval
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }

    // Attempt to reconnect
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      console.warn('[WebSocket] 🔴 WebSocket service is not responding.');
      console.warn('[WebSocket] 💡 Solution: Run "start-websocket-fixed.bat" to start the WebSocket service');
      this.updateConnectionStatus({
        connected: false,
        reconnecting: false,
        error: 'Max reconnection attempts reached - WebSocket service not running'
      });
      return;
    }

    this.reconnectAttempts++;
    this.updateConnectionStatus({ reconnecting: true });

    console.log(`[WebSocket] Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectDelay}ms`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.reconnectDelay);

    // Exponential backoff
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
  }

  private startPingInterval(): void {
    // Send ping every 30 seconds to keep connection alive
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, 30000);
  }

  private updateConnectionStatus(updates: Partial<ConnectionStatus>): void {
    this.connectionStatus = {
      ...this.connectionStatus,
      ...updates
    };

    // Notify callbacks
    this.statusChangeCallbacks.forEach(callback => {
      try {
        callback(this.connectionStatus);
      } catch (error) {
        console.error('Error in status change callback:', error);
      }
    });
  }
}

// Singleton instance
let wsClientInstance: WebSocketClient | null = null;

/**
 * Get or create WebSocket client instance.
 */
export function getWebSocketClient(userId: string): WebSocketClient {
  if (!wsClientInstance || wsClientInstance['userId'] !== userId) {
    if (wsClientInstance) {
      wsClientInstance.disconnect();
    }
    wsClientInstance = new WebSocketClient(userId);
  }
  return wsClientInstance;
}

/**
 * Disconnect and cleanup WebSocket client.
 */
export function disconnectWebSocket(): void {
  if (wsClientInstance) {
    wsClientInstance.disconnect();
    wsClientInstance = null;
  }
}
