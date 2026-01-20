import React from 'react';
import { useChat } from '@/contexts/ChatContext';
import { Button } from '@/components/ui/button';
import { CHAT_MODELS } from '@/lib/models';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  PlusCircle,
  MessageSquare,
  Settings2,
  Sparkles
} from 'lucide-react';

export const ChatSidebar: React.FC = () => {
  const {
    selectedModel,
    setSelectedModel,
    createNewConversation,
    conversations,
    loadConversation,
    conversationId,
  } = useChat();

  return (
    <div className="h-full flex flex-col bg-sidebar/30 backdrop-blur-xl border-r border-border/40">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-2 mb-4">
          {/* Logo */}
          <div className="w-8 h-8 rounded-lg overflow-hidden bg-sidebar-primary flex items-center justify-center">
            <img src="/logo2.png" alt="TrustMeBro! AI" className="w-full h-full object-cover" />
          </div>
          <span className="font-semibold text-sidebar-foreground">
            TrustMeBro! AI
          </span>
        </div>
        <Button
          onClick={createNewConversation}
          className="w-full justify-start gap-2"
          variant="secondary"
        >
          <PlusCircle className="w-4 h-4" />
          New Chat
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Model Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-sidebar-foreground flex items-center gap-2">
              <Settings2 className="w-4 h-4" />
              Model
            </label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-full bg-sidebar-accent/50 border-sidebar-border">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {CHAT_MODELS.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    <div className="flex flex-col">
                      <span className="font-medium">{model.label}</span>
                      {model.description && (
                        <span className="text-xs text-muted-foreground">
                          {model.description}
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Conversation History */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-sidebar-foreground flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              History
            </label>
            <div className="space-y-1">
              {conversations.length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">
                  No conversations yet
                </p>
              ) : (
                conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => loadConversation(conv.id)}
                    className={`w-full text-left p-2 rounded-md text-sm transition-colors ${conversationId === conv.id
                      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
                      }`}
                  >
                    {conv.title}
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
};
