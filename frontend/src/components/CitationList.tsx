import React from 'react';
import { Citation } from '../types';
import CitationCard from './CitationCard';

interface CitationListProps {
  citations: Citation[];
}

const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-amber-900 uppercase">📚 Sources ({citations.length})</p>
      <div className="space-y-2">
        {citations.map((citation) => (
          <CitationCard key={citation.index} citation={citation} index={citation.index} />
        ))}
      </div>
    </div>
  );
};

export default CitationList;
