import React, { useRef, useEffect } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Sparkles, LogOut, Loader2, Palette } from 'lucide-react';

export const ChatPanel: React.FC = () => {
  const { messages, isTyping, selectedModel } = useChat();
  const { logout, user } = useAuth();
  const { theme, setTheme } = useTheme();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="h-full flex flex-col bg-transparent relative">
      {/* Header - Glassmorphism */}
      <div className="flex items-center justify-between p-4 border-b border-border/40 bg-background/40 backdrop-blur-md sticky top-0 z-10 w-full">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary animate-pulse" />
          <h2 className="font-semibold text-lg bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            AI Workspace
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Model:</span>
          <span className="text-sm font-medium text-foreground">{selectedModel}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{user?.email}</span>

          {/* Theme Switcher */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="w-9 h-9">
                <Palette className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme('dark')}>
                🌙 Dark
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('light')}>
                ☀️ Light
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('benz')}>
                ✨ Benz
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button variant="ghost" size="sm" onClick={logout} className="gap-2">
            <LogOut className="w-4 h-4" />
            Sign out
          </Button>
        </div>
      </div>

      {/* Messages area */}
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isTyping && <TypingIndicator />}
            </>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <ChatInput />
    </div>
  );
};

const EmptyState: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-[60vh] text-center">
    <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
      <Sparkles className="w-8 h-8 text-primary" />
    </div>
    <h2 className="text-2xl font-semibold text-foreground mb-2">
      How can I help you today?
    </h2>
    <p className="text-muted-foreground max-w-md">
      Ask me anything. I can help with research, analysis, writing, coding, and much more.
    </p>
    <div className="grid grid-cols-2 gap-3 mt-8 max-w-lg">
      <SuggestionCard text="Explain quantum computing in simple terms" />
      <SuggestionCard text="Write a Python function to sort a list" />
      <SuggestionCard text="Help me plan a marketing strategy" />
      <SuggestionCard text="Summarize the latest AI research" />
    </div>
  </div>
);

const SuggestionCard: React.FC<{ text: string }> = ({ text }) => {
  const { sendMessage } = useChat();

  return (
    <button
      onClick={() => sendMessage(text)}
      className="p-4 text-left text-sm rounded-xl border border-border bg-card hover:bg-accent hover:border-primary/30 transition-all duration-200"
    >
      {text}
    </button>
  );
};

const TypingIndicator: React.FC = () => (
  <div className="flex items-center gap-2 text-muted-foreground">
    <Loader2 className="w-4 h-4 animate-spin" />
    <span className="text-sm">AI is thinking...</span>
  </div>
);
