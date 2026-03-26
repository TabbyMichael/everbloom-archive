// WebSocket service for real-time updates
import { io, Socket } from 'socket.io-client';

export interface CandleUpdate {
  tribute_id: string;
  candle_lit: boolean;
  timestamp: string;
}

export interface NewTribute {
  id: string;
  author_name: string;
  relation_to_deceased?: string;
  message: string;
  candle_lit: boolean;
  created_at: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private connected = false;

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve();
        return;
      }

      const serverUrl = import.meta.env.VITE_WS_URL || 'http://localhost:8000';
      
      this.socket = io(serverUrl, {
        transports: ['websocket', 'polling'],
        timeout: 5000,
      });

      this.socket.on('connect', () => {
        console.log('WebSocket connected');
        this.connected = true;
        resolve();
      });

      this.socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        this.connected = false;
      });

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        this.connected = false;
        reject(error);
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  isConnected(): boolean {
    return this.connected && this.socket?.connected || false;
  }

  // Join tributes room for real-time updates
  joinTributesRoom(): void {
    if (this.socket) {
      this.socket.emit('join_tributes');
      console.log('Joined tributes room');
    }
  }

  // Leave tributes room
  leaveTributesRoom(): void {
    if (this.socket) {
      this.socket.emit('leave_tributes');
      console.log('Left tributes room');
    }
  }

  // Listen for candle updates
  onCandleUpdate(callback: (data: CandleUpdate) => void): void {
    if (this.socket) {
      this.socket.on('candle_update', callback);
    }
  }

  // Listen for new tributes
  onNewTribute(callback: (data: NewTribute) => void): void {
    if (this.socket) {
      this.socket.on('new_tribute', callback);
    }
  }

  // Remove event listeners
  offCandleUpdate(callback?: (data: CandleUpdate) => void): void {
    if (this.socket) {
      this.socket.off('candle_update', callback);
    }
  }

  offNewTribute(callback?: (data: NewTribute) => void): void {
    if (this.socket) {
      this.socket.off('new_tribute', callback);
    }
  }

  // Generic event listener
  on(event: string, callback: (data: any) => void): void {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event: string, callback?: (data: any) => void): void {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }
}

// Singleton instance
export const websocketService = new WebSocketService();

// React hook for WebSocket
export const useWebSocket = () => {
  const connect = () => websocketService.connect();
  const disconnect = () => websocketService.disconnect();
  const isConnected = () => websocketService.isConnected();
  const joinTributesRoom = () => websocketService.joinTributesRoom();
  const leaveTributesRoom = () => websocketService.leaveTributesRoom();
  const onCandleUpdate = (callback: (data: CandleUpdate) => void) => websocketService.onCandleUpdate(callback);
  const onNewTribute = (callback: (data: NewTribute) => void) => websocketService.onNewTribute(callback);
  const offCandleUpdate = (callback?: (data: CandleUpdate) => void) => websocketService.offCandleUpdate(callback);
  const offNewTribute = (callback?: (data: NewTribute) => void) => websocketService.offNewTribute(callback);

  return {
    connect,
    disconnect,
    isConnected,
    joinTributesRoom,
    leaveTributesRoom,
    onCandleUpdate,
    onNewTribute,
    offCandleUpdate,
    offNewTribute,
  };
};
