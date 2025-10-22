import React, { useRef, useState } from 'react';
import { useDocumentStore } from '../stores/documentStore';
import { documentsAPI } from '../services/api';
import { Upload } from 'lucide-react';

interface DocumentUploadProps {
  onSuccess: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onSuccess }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setUploadProgress } = useDocumentStore();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files are supported');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await documentsAPI.upload(file);
      setUploadProgress(100);
      onSuccess();
    } catch (err) {
      setError('Failed to upload document');
      console.error(err);
    } finally {
      setUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="space-y-3">
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="mx-auto mb-2 text-gray-400" size={32} />
        <p className="text-sm font-medium text-gray-900">
          Click to upload or drag and drop
        </p>
        <p className="text-xs text-gray-500 mt-1">PDF files only</p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        disabled={uploading}
        className="hidden"
      />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 p-3 rounded text-sm">
          {error}
        </div>
      )}

      {uploading && (
        <div className="bg-blue-50 border border-blue-200 text-blue-600 p-3 rounded text-sm">
          Uploading...
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
