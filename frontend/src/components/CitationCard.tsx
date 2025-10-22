import React from 'react';
import { Citation } from '../types';
import { FileText } from 'lucide-react';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

const CitationCard: React.FC<CitationCardProps> = ({ citation, index }) => {
  return (
    <div className="flex items-start gap-2 text-xs bg-gray-50 p-2 rounded">
      <div className="flex-shrink-0">
        <FileText size={14} className="text-gray-600 mt-0.5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-700 truncate">{index}. {citation.source}</p>
        {citation.page && (
          <p className="text-gray-500">Page {citation.page}</p>
        )}
        {citation.confidence && (
          <p className="text-gray-500">
            Confidence: {(citation.confidence * 100).toFixed(0)}%
          </p>
        )}
      </div>
    </div>
  );
};

export default CitationCard;
