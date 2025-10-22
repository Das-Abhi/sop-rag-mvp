import React, { useEffect, useState } from 'react';
import { useDocumentStore } from '../stores/documentStore';
import { documentsAPI } from '../services/api';
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

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await documentsAPI.list();
      setDocuments(response.data.documents || []);
      setError(null);
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
