import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot } from 'lucide-react';

const Message = ({ text, isUser, sources, sources_meta, confidence, isError }) => {
  return (
    <div className={`flex w-full animate-slide-up ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] flex gap-4 p-4 rounded-2xl ${
        isUser 
          ? 'bg-blue-600/90 text-white rounded-br-sm' 
          : 'glass-panel rounded-bl-sm'
      }`}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center shrink-0 shadow-lg">
            <Bot size={18} className="text-white" />
          </div>
        )}
        
        <div className="flex flex-col flex-1 min-w-0">
          <div className={`prose prose-invert max-w-none text-sm md:text-base leading-relaxed ${isError ? 'text-red-400' : 'text-slate-200'}`}>
            <ReactMarkdown>{text}</ReactMarkdown>
          </div>

          {/* Confidence and structured sources */}
          {(confidence !== undefined && confidence !== null) && (
            <div className="text-xs text-slate-400 mt-2">Confidence: {(confidence*100).toFixed(0)}%</div>
          )}

          {Array.isArray(sources_meta) && sources_meta.length > 0 && (
            <div className="text-xs text-slate-300 mt-2">
              {sources_meta.length === 1 ? (
                <div>
                  <div className="font-medium">Source: {sources_meta[0].source}</div>
                  {sources_meta[0].chunk != null && <div>Chunk: {sources_meta[0].chunk}</div>}
                  {sources_meta[0].page != null && <div>Page: {sources_meta[0].page}</div>}
                  {sources_meta[0].similarity != null && <div>Similarity: {Number(sources_meta[0].similarity).toFixed(2)}</div>}
                </div>
              ) : (
                <div>
                  <div className="font-medium">Sources:</div>
                  <ul className="list-inside list-disc ml-4">
                    {sources_meta.map((s, idx) => (
                      <li key={idx}>
                        {s.source}{s.page != null ? ` (Page ${s.page})` : s.chunk != null ? ` (Chunk ${s.chunk})` : ''}{s.similarity != null ? ` — ${Number(s.similarity).toFixed(2)}` : ''}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {isUser && (
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center shrink-0">
            <User size={18} className="text-white" />
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
