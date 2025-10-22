import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import DocumentManager from './components/DocumentManager';
import { Menu, X } from 'lucide-react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="fixed bottom-4 right-4 z-50 md:hidden p-2 bg-blue-500 text-white rounded-full"
      >
        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Navigation Sidebar */}
      <nav
        className={`${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 transition-transform fixed md:relative w-64 h-full bg-gray-900 text-white p-4 z-40`}
      >
        <div className="mb-8">
          <h1 className="text-xl font-bold">SOP RAG MVP</h1>
          <p className="text-xs text-gray-400 mt-1">Document Intelligence</p>
        </div>

        <div className="space-y-2">
          <button
            onClick={() => {
              setActiveTab('chat');
              setMobileMenuOpen(false);
            }}
            className={`w-full text-left px-4 py-2 rounded transition-colors ${
              activeTab === 'chat'
                ? 'bg-blue-500 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            💬 Chat
          </button>
          <button
            onClick={() => {
              setActiveTab('documents');
              setMobileMenuOpen(false);
            }}
            className={`w-full text-left px-4 py-2 rounded transition-colors ${
              activeTab === 'documents'
                ? 'bg-blue-500 text-white'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            📄 Documents
          </button>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-700">
          <p className="text-xs text-gray-400">API</p>
          <p className="text-xs text-gray-500 mt-2">localhost:8000</p>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden md:ml-0">
        {activeTab === 'chat' ? <ChatInterface /> : <DocumentManager />}
      </main>
    </div>
  );
};

export default App;
