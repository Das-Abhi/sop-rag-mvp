import React, { useState } from 'react';
import { Document } from '../types';
import { useChatStore } from '../stores/chatStore';
import { documentsAPI } from '../services/api';
import { Trash2, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface DocumentCardProps {
  document: Document;
  onRefresh: () => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ document, onRefresh }) => {
  const { selectDocument, deselectDocument, selectedDocuments } = useChatStore();
  const [deleting, setDeleting] = useState(false);
  const isSelected = selectedDocuments.includes(document.document_id);

  const handleToggleSelect = () => {
    if (isSelected) {
      deselectDocument(document.document_id);
    } else {
      selectDocument(document.document_id);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    setDeleting(true);
    try {
      await documentsAPI.delete(document.document_id);
      onRefresh();
    } catch (error) {
      alert('Failed to delete document');
      console.error(error);
    } finally {
      setDeleting(false);
    }
  };

  const getStatusIcon = () => {
    switch (document.status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'processing':
        return <Clock className="text-blue-500 animate-spin" size={20} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />;
      default:
        return <Clock className="text-gray-400" size={20} />;
    }
  };

  return (
    <div
      className={`border rounded-lg p-4 cursor-pointer transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={handleToggleSelect}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3 flex-1">
          {getStatusIcon()}
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 break-words">{document.title}</h3>
            <p className="text-sm text-gray-500 capitalize mt-1">
              {document.status}
            </p>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete();
          }}
          disabled={deleting}
          className="text-gray-400 hover:text-red-500 disabled:opacity-50"
        >
          <Trash2 size={18} />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 text-xs bg-gray-50 rounded p-2">
        <div>
          <p className="text-gray-500">Text Chunks</p>
          <p className="font-semibold text-gray-900">{document.text_chunks}</p>
        </div>
        <div>
          <p className="text-gray-500">Images</p>
          <p className="font-semibold text-gray-900">{document.image_chunks}</p>
        </div>
        <div>
          <p className="text-gray-500">Tables</p>
          <p className="font-semibold text-gray-900">{document.table_chunks}</p>
        </div>
      </div>

      {/* Date */}
      <p className="text-xs text-gray-400 mt-2">
        {new Date(document.created_at).toLocaleDateString()}
      </p>
    </div>
  );
};

export default DocumentCard;
