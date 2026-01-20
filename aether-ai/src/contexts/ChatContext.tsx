import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ChatMessage, Conversation, MCPPlugin } from '@/types';
import { CHAT_MODELS } from '@/lib/models';

interface ChatContextType {
  conversationId: string | null;
  selectedModel: string;
  messages: ChatMessage[];
  useRag: boolean;
  webSearchEnabled: boolean;
  imageGenEnabled: boolean;
  conversations: Conversation[];
  isTyping: boolean;
  mcpPlugins: MCPPlugin[];
  setSelectedModel: (model: string) => void;
  setUseRag: (value: boolean) => void;
  setWebSearchEnabled: (value: boolean) => void;
  setImageGenEnabled: (value: boolean) => void;
  toggleMcp: (mcpId: string) => void;
  toggleTool: (mcpId: string, toolId: string) => void;
  sendMessage: (content: string, attachments?: any[]) => Promise<void>;
  uploadDocument: (file: File) => Promise<any>;
  createNewConversation: () => void;
  loadConversation: (id: string) => void;
}

const defaultMcpPlugins: MCPPlugin[] = [
  {
    id: 'notion',
    name: 'Notion',
    enabled: false,
    tools: [
      { id: 'search_pages', name: 'Search Pages', enabled: true },
      { id: 'get_page', name: 'Get Page', enabled: true },
      { id: 'create_page', name: 'Create Page', enabled: true },
      { id: 'update_page', name: 'Update Page', enabled: true },
    ],
  },
  {
    id: 'gmail',
    name: 'Gmail',
    enabled: false,
    tools: [
      { id: 'read_email', name: 'Read Email', enabled: true },
      { id: 'send_email', name: 'Send Email', enabled: true },
      { id: 'search_emails', name: 'Search Emails', enabled: true },
      { id: 'filter_emails', name: 'Filter Emails', enabled: true },
    ],
  },
  {
    id: 'google-calendar',
    name: 'Google Calendar',
    enabled: false,
    tools: [
      { id: 'list_events', name: 'List Events', enabled: true },
      { id: 'get_event', name: 'Get Event', enabled: true },
      { id: 'create_event', name: 'Create Event', enabled: true },
      { id: 'update_event', name: 'Update Event', enabled: true },
      { id: 'delete_event', name: 'Delete Event', enabled: true },
    ],
  },
  {
    id: 'n8n',
    name: 'n8n',
    enabled: false,
    tools: [
      { id: 'trigger_workflow', name: 'Trigger Workflow', enabled: true },
      { id: 'list_workflows', name: 'List Workflows', enabled: true },
      { id: 'get_execution', name: 'Get Execution', enabled: false },
    ],
  },
];

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState(CHAT_MODELS[0].id);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [useRag, setUseRag] = useState(false);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [imageGenEnabled, setImageGenEnabled] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [mcpPlugins, setMcpPlugins] = useState<MCPPlugin[]>(defaultMcpPlugins);

  const fetchConversations = useCallback(async () => {
    try {
      const response = await fetch('/api/conversations');
      if (response.ok) {
        const data = await response.json();
        // Map backend response to frontend types
        const backendConversations = data.conversations || [];
        const mappedConversations: Conversation[] = backendConversations.map((c: any) => ({
          id: c.conversation_id, // Map conversation_id to id
          title: c.title || 'New Conversation',
          date: new Date(c.created_at || c.updated_at || Date.now()),
          messages: (c.messages || []).map((m: any) => ({
            id: crypto.randomUUID(), // Generate ID for message
            role: m.role,
            content: m.content,
            timestamp: new Date(m.timestamp),
          })),
        }));

        // Sort by date desc
        mappedConversations.sort((a, b) => b.date.getTime() - a.date.getTime());
        setConversations(mappedConversations);
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  }, []);

  // Fetch conversations on mount
  React.useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  const toggleMcp = useCallback((mcpId: string) => {
    setMcpPlugins((prev) =>
      prev.map((mcp) =>
        mcp.id === mcpId ? { ...mcp, enabled: !mcp.enabled } : mcp
      )
    );
  }, []);

  const toggleTool = useCallback((mcpId: string, toolId: string) => {
    setMcpPlugins((prev) =>
      prev.map((mcp) =>
        mcp.id === mcpId
          ? {
            ...mcp,
            tools: mcp.tools.map((tool) =>
              tool.id === toolId ? { ...tool, enabled: !tool.enabled } : tool
            ),
          }
          : mcp
      )
    );
  }, []);

  const sendMessage = useCallback(async (content: string, attachments: any[] = []) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
      attachments,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    const enabledMcps = mcpPlugins.filter((m) => m.enabled);
    const enabledTools = enabledMcps.reduce((acc, mcp) => {
      acc[mcp.id] = mcp.tools.filter((t) => t.enabled).map((t) => t.id);
      return acc;
    }, {} as Record<string, string[]>);

    // Generate conversation_id if it doesn't exist
    let currentConversationId = conversationId;
    if (!currentConversationId) {
      currentConversationId = crypto.randomUUID();
      setConversationId(currentConversationId);
    }

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: currentConversationId,
          model: selectedModel,
          use_rag: useRag,
          web_search: webSearchEnabled,
          image_generation: imageGenEnabled,
          enabled_mcps: enabledMcps.map((m) => m.id),
          enabled_tools: enabledTools,
          message: content,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: data.message,
          timestamp: new Date(),
          sources: data.sources,
          toolsUsed: data.tools_used,
          imageUrl: data.image_url,
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Refresh conversations
        fetchConversations();
      } else {
        // Handle API errors (429, 500, etc)
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        console.error('API Error:', errorData);

        const errorMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `⚠️ Error: ${errorData.detail || 'Failed to get response from AI.'}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (e) {
      console.error('Network Error:', e);
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠️ Network Error: Unable to reach the server. Please check your connection.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [conversationId, selectedModel, useRag, webSearchEnabled, imageGenEnabled, mcpPlugins, fetchConversations]);

  const uploadDocument = useCallback(async (file: File) => {
    let currentConversationId = conversationId;
    if (!currentConversationId) {
      currentConversationId = crypto.randomUUID();
      setConversationId(currentConversationId);
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('conversation_id', currentConversationId);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();

      // Auto-enable RAG when doc uploaded
      setUseRag(true);

      return data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }, [conversationId]);

  const createNewConversation = useCallback(() => {
    // If we have messages, ensure they are saved (already done via sendMessage backend call)
    // Just reset the state for a new one
    setConversationId(null); // Set to null to generate new one on first message
    setMessages([]);
    fetchConversations(); // Refresh list to ensure previous one appears
  }, [fetchConversations]);

  const loadConversation = useCallback(async (id: string) => {
    // Try to fetch full details from backend
    try {
      const response = await fetch(`/api/conversations/${id}`);
      if (response.ok) {
        const data = await response.json();
        setConversationId(data.conversation_id); // Map conversation_id

        // Map messages
        const mappedMessages = (data.messages || []).map((m: any) => ({
          id: crypto.randomUUID(),
          role: m.role,
          content: m.content,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(mappedMessages);
      } else {
        // Fallback to local list if backend detail fetch fails
        const conversation = conversations.find((c) => c.id === id);
        if (conversation) {
          setConversationId(id);
          setMessages(conversation.messages);
        }
      }
    } catch (e) {
      console.error("Error loading conversation", e);
    }
  }, [conversations]);

  return (
    <ChatContext.Provider
      value={{
        conversationId,
        selectedModel,
        messages,
        useRag,
        webSearchEnabled,
        imageGenEnabled,
        conversations,
        isTyping,
        mcpPlugins,
        setSelectedModel,
        setUseRag,
        setWebSearchEnabled,
        setImageGenEnabled,
        toggleMcp,
        toggleTool,
        sendMessage,
        uploadDocument,
        createNewConversation,
        loadConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
