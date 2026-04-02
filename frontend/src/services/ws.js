export class SocketService {
  constructor(roomId, username, displayName, onMessage, onOpen, onClose, onError) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = import.meta.env.VITE_WS_BASE || `${protocol}//${window.location.host}`;

    this.socket = new WebSocket(
      `${baseUrl}/ws/rooms/${encodeURIComponent(roomId)}?username=${encodeURIComponent(username)}&displayName=${encodeURIComponent(displayName || username)}`
    );

    this.socket.onopen = () => {
      if (onOpen) onOpen();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Invalid WebSocket message:', error);
      }
    };

    this.socket.onclose = () => {
      if (onClose) onClose();
    };

    this.socket.onerror = (error) => {
      if (onError) onError(error);
    };
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  close() {
    if (this.socket) {
      this.socket.close();
    }
  }
}