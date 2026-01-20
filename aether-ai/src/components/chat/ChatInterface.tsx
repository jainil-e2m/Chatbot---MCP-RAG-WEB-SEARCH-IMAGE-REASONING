import React from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatPanel } from './ChatPanel';

export const ChatInterface: React.FC = () => {
  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <div className="w-72 flex-shrink-0 hidden md:block">
        <ChatSidebar />
      </div>
      
      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatPanel />
      </div>
    </div>
  );
};
