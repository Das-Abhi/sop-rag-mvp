import React, { useEffect, useState, useRef } from 'react';
import { useDocumentStore } from '../stores/documentStore';
import { documentsAPI } from '../services/api';
import { Document } from '../types';
import DocumentList from './DocumentList';
import DocumentUpload from './DocumentUpload';

const DocumentManager: React.FC = () => {
  const {
    documents,
    loading,
    error,
    setDocuments,
    setLoading,
    setError,
  } = useDocumentStore();
  const [showUpload, setShowUpload] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchDocuments();
    setupWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await documentsAPI.list();
      const docs = response.data.documents || [];
      setDocuments(docs);
      setError(null);

      // Subscribe to updates for all documents
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        docs.forEach(doc => {
          wsRef.current?.send(JSON.stringify({
            action: 'subscribe',
            document_id: doc.document_id
          }));
        });
      }
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = async () => {
    setShowUpload(false);
    await fetchDocuments();
  };

  const setupWebSocket = () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        // Document subscriptions will be set up when documents are fetched
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const { type, document_id, status, progress, current_step } = message;

          // Handle subscription confirmation
          if (type === 'subscription_confirmed') {
            console.log(`Subscribed to document: ${document_id}`);
            return;
          }

          // Handle processing update messages
          if (type === 'processing_update') {
            console.log(`Document ${document_id}: ${status} (${progress}%) - ${current_step}`);

            // Update the document in the store
            setDocuments((prevDocs: Document[]) => prevDocs.map((doc: Document) => {
              if (doc.document_id === document_id) {
                return {
                  ...doc,
                  status
                };
              }
              return doc;
            }));
          }

          // Handle document status messages (sent on subscribe)
          if (type === 'document_status') {
            console.log(`Document ${document_id} status: ${status}`);

            setDocuments((prevDocs: Document[]) => prevDocs.map((doc: Document) => {
              if (doc.document_id === document_id) {
                return {
                  ...doc,
                  status
                };
              }
              return doc;
            }));
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt to reconnect after 3 seconds
        setTimeout(() => setupWebSocket(), 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to setup WebSocket:', error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          {showUpload ? 'Cancel' : 'Upload Document'}
        </button>
      </div>

      {/* Upload Section */}
      {showUpload && (
        <div className="border-b border-gray-200 p-4">
          <DocumentUpload onSuccess={handleUploadSuccess} />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 p-4 m-4 rounded">
          {error}
        </div>
      )}

      {/* Document List */}
      <div className="flex-1 overflow-auto">
        <DocumentList documents={documents} loading={loading} onRefresh={fetchDocuments} />
      </div>
    </div>
  );
};

export default DocumentManager;
