import React from 'react';
import { Citation } from '../types';
import { FileText } from 'lucide-react';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

const CitationCard: React.FC<CitationCardProps> = ({ citation }) => {
  const confidencePercent = Math.round((citation.confidence || 0) * 100);

  return (
    <div className="flex items-start gap-2 text-xs bg-amber-50 border border-amber-200 p-3 rounded hover:bg-amber-100 transition-colors cursor-pointer">
      <div className="flex-shrink-0">
        <FileText size={14} className="text-amber-600 mt-0.5" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className="font-medium text-amber-900 truncate">[{citation.index}] {citation.source}</p>
          {citation.confidence !== undefined && (
            <span className="text-xs font-semibold text-amber-700 whitespace-nowrap bg-amber-100 px-2 py-0.5 rounded">
              {confidencePercent}%
            </span>
          )}
        </div>
        <div className="flex gap-2 mt-1 text-amber-700">
          {citation.page && (
            <p className="text-xs">📄 Page {citation.page}</p>
          )}
        </div>
        <p className="text-amber-700 text-xs mt-1 line-clamp-2">
          {citation.content_preview}
        </p>
      </div>
    </div>
  );
};

export default CitationCard;
