import React from 'react';
import { Citation } from '../types';
import { FileText } from 'lucide-react';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

const CitationCard: React.FC<CitationCardProps> = ({ citation }) => {
  return (
    <div className="flex items-start gap-2 text-xs bg-amber-50 border border-amber-200 p-3 rounded hover:bg-amber-100 transition-colors cursor-pointer">
      <div className="flex-shrink-0">
        <FileText size={14} className="text-amber-600 mt-0.5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-amber-900 truncate">[{citation.index}] {citation.source}</p>
        {citation.page && (
          <p className="text-amber-700 text-xs">Page {citation.page}</p>
        )}
        <p className="text-amber-700 text-xs mt-1 line-clamp-2">
          {citation.content_preview}
        </p>
      </div>
    </div>
  );
};

export default CitationCard;
