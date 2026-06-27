import { Badge, StatCard, ProgressBar } from './components.js';

class DashboardDataClient {
  constructor(baseURL = '') {
    this.sseConnection = null;
    this.pollingInterval = null;
    this.lastData = null;
    this.isConnected = false;
    this.baseURL = baseURL;
  }

  connect(onData, onError) {
    this.trySSE(onData, onError);
    setTimeout(() => {
      if (!this.isConnected) {
        console.log('SSE failed, falling back to polling');
        this.startPolling(onData, onError);
      }
    }, 8000);
  }

  trySSE(onData, onError) {
    try {
      this.sseConnection = new EventSource(`${this.baseURL}/events`);
      this.sseConnection.onopen = () => {
        this.isConnected = true;
        console.log('SSE connected');
      };
      this.sseConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.lastData = data;
          onData(data);
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      };
      this.sseConnection.onerror = (error) => {
        console.error('SSE error:', error);
        this.sseConnection.close();
        this.isConnected = false;
        if (this.pollingInterval) {
          this.startPolling(onData, onError);
        }
      };
    } catch (e) {
      console.error('SSE not supported, using polling');
      if (this.pollingInterval) {
        this.startPolling(onData, onError);
      }
    }
  }

  startPolling(onData, onError) {
    if (this.pollingInterval) return;
    const poll = async () => {
      try {
        const response = await fetch(`${this.baseURL}/api/stats`);
        if (response.ok) {
          const data = await response.json();
          this.lastData = data;
          onData(data);
        }
      } catch (e) {
        console.error('Polling error:', e);
        if (onError) onError(e);
      }
    };
    poll();
    this.pollingInterval = setInterval(poll, 8000);
  }

  disconnect() {
    if (this.sseConnection) {
      this.sseConnection.close();
    }
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
    this.isConnected = false;
  }
}

export { DashboardDataClient };