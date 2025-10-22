import React, { useEffect, useRef, useState } from 'react';
import { useChatStore } from '../stores/chatStore';
import { useDocumentStore } from '../stores/documentStore';
import { queryAPI, createWebSocketConnection, WebSocketActions } from '../services/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { Message } from '../types';

const ChatInterface: React.FC = () => {
  const { messages, addMessage, loading, setLoading, selectedDocuments } = useChatStore();
  const { documents } = useDocumentStore();
  const [ws, setWs] = useState<WebSocket | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket
  useEffect(() => {
    try {
      const websocket = createWebSocketConnection();
      wsRef.current = websocket;
      setWs(websocket);

      websocket.onopen = () => {
        console.log('WebSocket connected');
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      return () => {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.close();
        }
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, []);

  const handleSendMessage = async (query: string) => {
    if (!query.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: query,
      timestamp: new Date(),
    };
    addMessage(userMessage);
    setLoading(true);

    try {
      const response = await queryAPI.submit(query, selectedDocuments);
      const { query_id, response_text, citations, latency_ms } = response.data;

      const assistantMessage: Message = {
        id: query_id,
        type: 'assistant',
        content: response_text,
        citations,
        timestamp: new Date(),
      };
      addMessage(assistantMessage);
    } catch (error) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: 'Sorry, there was an error processing your query.',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
      console.error('Query error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <h1 className="text-2xl font-bold text-gray-900">SOP RAG Chat</h1>
        <p className="text-sm text-gray-600">
          {selectedDocuments.length > 0
            ? `Using ${selectedDocuments.length} document(s)`
            : 'No documents selected'}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={loading || selectedDocuments.length === 0}
          placeholder={
            selectedDocuments.length === 0
              ? 'Please select documents first...'
              : 'Ask a question...'
          }
        />
      </div>
    </div>
  );
};

export default ChatInterface;
