import React from 'react';
import { BookOpen } from 'lucide-react';

const SourceReferences = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
      <div className="flex items-center gap-2 text-sm text-blue-400 font-medium mb-3">
        <BookOpen size={16} />
        <span>Source References</span>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {sources.map((source, idx) => (
          <div key={idx} className="bg-slate-800/50 rounded-lg p-3 border border-slate-700 hover:border-slate-600 transition-colors">
            <h4 className="text-sm font-semibold text-slate-200 mb-1">{source.document_name}</h4>
            <p className="text-xs text-slate-400 line-clamp-2 italic">"{source.snippet}"</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SourceReferences;
