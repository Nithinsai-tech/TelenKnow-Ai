import React from 'react';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="min-h-screen bg-slate-900 bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop')] bg-cover bg-center bg-no-repeat bg-fixed flex items-center justify-center p-4 sm:p-8">
      {/* Dark overlay for better contrast */}
      <div className="fixed inset-0 bg-slate-950/80 z-0"></div>
      
      {/* Decorative background blobs */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl -translate-y-1/2 z-0"></div>
      <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl translate-y-1/2 z-0"></div>
      
      <div className="w-full h-[90vh] z-10 relative">
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
