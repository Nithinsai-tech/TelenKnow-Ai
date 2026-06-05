import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Database } from 'lucide-react';
import Message from './Message';
import { queryDocuments, indexSampleDocs } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      text: "Hello! I'm TeleKnow AI, your technical support assistant. How can I help you today?",
      isUser: false
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleIndexDocs = async () => {
    setIsIndexing(true);
    try {
      const res = await indexSampleDocs();
      alert(res.message + ' ' + JSON.stringify(res.details));
    } catch (err) {
      alert("Error indexing documents: " + err.message);
    } finally {
      setIsIndexing(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { id: Date.now().toString(), text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Format existing messages (excluding the first welcome message and any errors) into chat history
      const chatHistory = messages
        .filter(m => m.id !== 'welcome' && !m.isError)
        .map(m => ({
          role: m.isUser ? 'user' : 'ai',
          content: m.text
        }));

      const response = await queryDocuments(userMessage.text, chatHistory);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: response.answer,
        isUser: false,
        sources: response.sources,
        sources_meta: response.sources_meta || response.sources || [],
        confidence: response.confidence
      }]);
    } catch (error) {
      console.error("Error querying:", error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: "I'm sorry, I encountered an error connecting to the server. Please ensure the backend is running.",
        isUser: false,
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full max-w-5xl mx-auto overflow-hidden animate-fade-in relative">
      
      {/* Header */}
      <div className="glass-panel rounded-t-3xl rounded-b-none border-b-0 p-6 flex justify-between items-center z-10">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            TeleKnow AI
          </h1>
          <p className="text-sm text-slate-400">Telecom Knowledge Navigator</p>
        </div>
        <button 
          onClick={handleIndexDocs}
          disabled={isIndexing}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 hover:bg-slate-700 transition-colors text-sm font-medium"
        >
          {isIndexing ? <Loader2 size={16} className="animate-spin" /> : <Database size={16} className="text-purple-400" />}
          <span>{isIndexing ? 'Indexing...' : 'Index Sample Docs'}</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 glass-panel rounded-none border-y-0 p-6 overflow-y-auto scrollbar-hide flex flex-col gap-6">
        {messages.map((msg) => (
          <Message 
            key={msg.id} 
            text={msg.text} 
            isUser={msg.isUser} 
            sources={msg.sources} 
            isError={msg.isError} 
          />
        ))}
        {isLoading && (
          <div className="flex justify-start animate-slide-up">
            <div className="glass-panel p-4 rounded-2xl rounded-bl-sm flex gap-3 items-center">
              <Loader2 className="animate-spin text-blue-400" size={20} />
              <span className="text-sm text-slate-300">Searching telecom documentation...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="glass-panel rounded-b-3xl rounded-t-none border-t-0 p-4 z-10">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about telecom configuration, troubleshooting..."
            className="w-full glass-input rounded-2xl py-4 pl-6 pr-16 text-sm"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 transition-colors text-white shadow-lg"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
      
    </div>
  );
};

export default ChatInterface;
