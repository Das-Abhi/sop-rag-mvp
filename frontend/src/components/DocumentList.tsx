import React from 'react';
import { Document } from '../types';
import DocumentCard from './DocumentCard';
import { RefreshCw } from 'lucide-react';

interface DocumentListProps {
  documents: Document[];
  loading: boolean;
  onRefresh: () => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, loading, onRefresh }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading documents...</div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <p className="mb-4">No documents uploaded yet</p>
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {documents.map((doc) => (
        <DocumentCard key={doc.document_id} document={doc} onRefresh={onRefresh} />
      ))}
    </div>
  );
};

export default DocumentList;
