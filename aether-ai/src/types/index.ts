export interface Attachment {
  type: 'image' | 'file';
  url: string;
  name: string;
  mimeType?: string;
  size?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  imageUrl?: string;
  toolsUsed?: string[];
  attachments?: Attachment[];
}

export interface Source {
  title: string;
  url: string;
  snippet?: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  date: Date;
  messages: ChatMessage[];
}

export interface MCPPlugin {
  id: string;
  name: string;
  enabled: boolean;
  tools: Tool[];
}

export interface Tool {
  id: string;
  name: string;
  enabled: boolean;
}

export interface AppState {
  isAuthenticated: boolean;
  userId: string | null;
  conversationId: string | null;
  selectedModel: string;
  enabledMcps: string[];
  enabledTools: Record<string, string[]>;
  messages: ChatMessage[];
  useRag: boolean;
  conversations: Conversation[];
}

export interface User {
  id: string;
  email: string;
  name?: string;
  token: string;
}
