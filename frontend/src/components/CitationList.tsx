import React from 'react';
import { Citation } from '../types';
import CitationCard from './CitationCard';

interface CitationListProps {
  citations: Citation[];
}

const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold text-gray-600 uppercase">Sources</p>
      <div className="space-y-1">
        {citations.map((citation, idx) => (
          <CitationCard key={idx} citation={citation} index={idx + 1} />
        ))}
      </div>
    </div>
  );
};

export default CitationList;
