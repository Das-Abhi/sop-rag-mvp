import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document endpoints
export const documentsAPI = {
  list: () => api.get('/documents'),
  get: (id: string) => api.get(`/documents/${id}`),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id: string) => api.delete(`/documents/${id}`),
  updateStatus: (id: string, status: string) =>
    api.put(`/documents/${id}/status`, { status }),
};

// Query endpoints
export const queryAPI = {
  submit: (queryText: string, documentIds?: string[]) =>
    api.post('/query', { query_text: queryText, document_ids: documentIds }),
  retrieve: (queryText: string, documentIds?: string[]) =>
    api.post('/query/retrieve', { query_text: queryText, document_ids: documentIds }),
  health: () => api.get('/query/health'),
};

// Processing endpoints
export const processingAPI = {
  getStatus: (taskId: string) => api.get(`/processing/status/${taskId}`),
  health: () => api.get('/processing/health'),
  vectorStoreStats: () => api.get('/processing/vector-store-stats'),
  clearCache: () => api.post('/processing/clear-cache'),
};

// WebSocket connection
export const createWebSocketConnection = () => {
  return new WebSocket(`${WS_BASE}/ws`);
};

export const WebSocketActions = {
  SUBSCRIBE: 'subscribe',
  UNSUBSCRIBE: 'unsubscribe',
  STATUS: 'status',
  PING: 'ping',
};

export const WebSocketMessageTypes = {
  PROCESSING_UPDATE: 'processing_update',
  CHAT_CHUNK: 'chat_chunk',
  QUERY_RESPONSE: 'query_response',
  ERROR: 'error',
};
