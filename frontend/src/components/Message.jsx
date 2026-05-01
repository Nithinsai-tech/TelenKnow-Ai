import React from 'react';
import { User, Bot } from 'lucide-react';

const Message = ({ text, isUser, sources, isError }) => {
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
            {text}
          </div>
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
