import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Send,
  Loader2,
  FileText,
  Upload,
  X,
  Puzzle,
  StickyNote,
  Mail,
  Calendar,
  Workflow,
  Sparkles,
  Search,
  Globe,
  Paperclip
} from 'lucide-react';

const mcpIcons: Record<string, React.ElementType> = {
  notion: StickyNote,
  gmail: Mail,
  google_calendar: Calendar,
  n8n: Workflow,
};

const mcpTooltips: Record<string, string> = {
  notion: "Manage Notion pages & databases",
  gmail: "Read, send & filter emails",
  "google-calendar": "Manage events & schedules", // Quotes for hyphens
  n8n: "Trigger workflows & automations"
};

export const ChatInput: React.FC = () => {
  const {
    sendMessage,
    isTyping,
    useRag,
    setUseRag,
    webSearchEnabled,
    setWebSearchEnabled,
    imageGenEnabled,
    setImageGenEnabled,
    mcpPlugins,
    toggleMcp,
    toggleTool,
    uploadDocument,
  } = useChat();
  const [input, setInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [attachments, setAttachments] = useState<any[]>([]);
  const [isRagPopoverOpen, setIsRagPopoverOpen] = useState(false);
  const [isMcpPopoverOpen, setIsMcpPopoverOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const enabledMcpCount = mcpPlugins.filter((m) => m.enabled).length;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = async () => {
    if ((!input.trim() && attachments.length === 0) || isTyping) return;
    const message = input.trim();
    const currentAttachments = [...attachments];

    setInput('');
    setAttachments([]);
    setUploadedFiles([]);

    await sendMessage(message, currentAttachments);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setUploadedFiles((prev) => [...prev, ...files]);

    for (const file of files) {
      // Auto-enable RAG for documents, but NOT for images
      if (!file.type.startsWith('image/')) {
        setUseRag(true);
      }

      try {
        const data = await uploadDocument(file);

        if (data) {
          setAttachments(prev => [...prev, {
            type: data.type === 'image' ? 'image' : 'file',
            url: data.image_data || null,
            name: data.filename,
            mimeType: file.type
          }]);
        }
      } catch (error) {
        console.error("Failed to upload file:", file.name, error);
      }
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="p-6 relative z-10 w-full max-w-4xl mx-auto">
      <div className={`relative transition-all duration-300 ${isRagPopoverOpen || isMcpPopoverOpen ? 'z-20' : ''
        }`}>
        <div className={`
          relative flex flex-col gap-2 p-3
          bg-background/40 backdrop-blur-xl
          border border-white/10 shadow-2xl
          rounded-3xl transition-all duration-300
          hover:bg-background/50 hover:border-white/20
          group
        `}>
          {/* Uploaded Files Preview */}
          {(uploadedFiles.length > 0 || attachments.length > 0) && (
            <div className="flex gap-2 px-2 pb-2 overflow-x-auto">
              {uploadedFiles.map((file, i) => (
                <div key={`file-${i}`} className="relative group/file animate-in fade-in zoom-in duration-200">
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-background/50 rounded-full border border-border/50 text-xs backdrop-blur-md">
                    <span className="max-w-[100px] truncate">{file.name}</span>
                    <button
                      onClick={() => removeFile(i)}
                      className="p-0.5 hover:bg-background/50 rounded-full transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
              {attachments.map((att, i) => (
                <div key={`att-${i}`} className="relative group/file animate-in fade-in zoom-in duration-200">
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full border border-primary/20 text-xs text-primary backdrop-blur-md">
                    <span className="max-w-[100px] truncate">{att.name}</span>
                    <button
                      onClick={() => removeFile(i)}
                      className="p-0.5 hover:bg-primary/20 rounded-full transition-colors"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-end gap-2">
            {/* Tool Toggles - Left Side */}
            <div className="flex items-center gap-1 pb-1">

              {/* 1. MCP Plugins (Puzzle) */}
              <TooltipProvider>
                <Tooltip>
                  <Popover open={isMcpPopoverOpen} onOpenChange={setIsMcpPopoverOpen}>
                    <PopoverTrigger asChild>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={`h-9 w-9 rounded-full transition-all duration-300 ${enabledMcpCount > 0
                              ? 'bg-primary/20 text-primary hover:bg-primary/30 shadow-[0_0_15px_rgba(var(--primary),0.3)]'
                              : 'text-muted-foreground hover:bg-white/10 hover:text-foreground'
                            }`}
                        >
                          <Puzzle className="w-5 h-5" />
                        </Button>
                      </TooltipTrigger>
                    </PopoverTrigger>
                    <PopoverContent
                      className="w-80 p-0 bg-background/80 backdrop-blur-xl border-white/10 shadow-2xl overflow-hidden"
                      side="top"
                      align="start"
                    >
                      <div className="p-4 border-b border-white/5">
                        <h4 className="font-medium flex items-center gap-2">
                          <Puzzle className="w-4 h-4 text-primary" />
                          MCP Plugins
                        </h4>
                        <p className="text-[10px] text-muted-foreground mt-1">
                          Connect external tools and services
                        </p>
                      </div>

                      <Accordion type="single" collapsible className="w-full max-h-[300px] overflow-y-auto">
                        {mcpPlugins.map((plugin) => (
                          <AccordionItem key={plugin.id} value={plugin.id} className="border-b border-white/5 px-4">
                            <div className="flex items-center justify-between py-2">
                              {/* Tooltip for Row */}
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <AccordionTrigger className="hover:no-underline py-0 flex-1 text-sm font-medium">
                                      <div className="flex items-center gap-2 text-left">
                                        {mcpIcons[plugin.id] && React.createElement(mcpIcons[plugin.id], { className: "w-4 h-4 text-muted-foreground" })}
                                        <span>{plugin.name}</span>
                                      </div>
                                    </AccordionTrigger>
                                  </TooltipTrigger>
                                  <TooltipContent side="right">
                                    <p>{mcpTooltips[plugin.id] || "MCP Plugin"}</p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>

                              <div className="ml-2 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                <Switch
                                  checked={plugin.enabled}
                                  onCheckedChange={() => toggleMcp(plugin.id)}
                                  className="scale-75"
                                />
                              </div>
                            </div>

                            <AccordionContent>
                              <div className="pl-6 space-y-2 pb-2">
                                {plugin.tools.map((tool: any) => (
                                  <div key={tool.id} className="flex items-center justify-between group">
                                    <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors">{tool.name}</span>
                                    <Switch
                                      checked={tool.enabled}
                                      onCheckedChange={() => toggleTool(plugin.id, tool.id)}
                                      disabled={!plugin.enabled}
                                      className="scale-75"
                                    />
                                  </div>
                                ))}
                                {(!plugin.tools || plugin.tools.length === 0) && (
                                  <p className="text-[10px] text-muted-foreground italic">No tools available</p>
                                )}
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        ))}
                      </Accordion>
                    </PopoverContent>
                  </Popover>
                  <TooltipContent>MCP Plugins</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {/* 2. Web Search (Globe) */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setWebSearchEnabled(!webSearchEnabled)}
                      className={`h-9 w-9 rounded-full transition-all duration-300 ${webSearchEnabled
                          ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                          : 'text-muted-foreground hover:bg-white/10 hover:text-foreground'
                        }`}
                    >
                      <Globe className="w-5 h-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="bg-black/90 border-white/10 backdrop-blur-md text-white">
                    <p className="font-medium">Web Search</p>
                    <p className="text-xs text-muted-foreground">Search the internet</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {/* 3. Image Gen (Sparkles) */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setImageGenEnabled(!imageGenEnabled)}
                      className={`h-9 w-9 rounded-full transition-all duration-300 ${imageGenEnabled
                          ? 'bg-gradient-to-r from-pink-500/20 to-purple-500/20 text-pink-400 hover:from-pink-500/30 hover:to-purple-500/30 border border-pink-500/20 shadow-[0_0_15px_rgba(236,72,153,0.3)]'
                          : 'text-muted-foreground hover:bg-white/10 hover:text-foreground'
                        }`}
                    >
                      <Sparkles className="w-5 h-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="bg-black/90 border-white/10 backdrop-blur-md text-white">
                    <p className="font-medium">Image Generation</p>
                    <p className="text-xs text-muted-foreground">Model: Gemini 2.5 Flash</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {/* 4. Upload & RAG (Paperclip) - Merged */}
              <TooltipProvider>
                <Tooltip>
                  <Popover>
                    <PopoverTrigger asChild>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={`h-9 w-9 rounded-full transition-all duration-300 ${useRag
                              ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20 shadow-[0_0_10px_rgba(245,158,11,0.2)]'
                              : 'text-muted-foreground hover:bg-white/10 hover:text-foreground'
                            }`}
                        >
                          <Paperclip className="w-5 h-5" />
                        </Button>
                      </TooltipTrigger>
                    </PopoverTrigger>
                    <PopoverContent className="w-64 p-3 bg-background/80 backdrop-blur-xl border-white/10 shadow-2xl" side="top" align="start">
                      <div className="space-y-4">
                        {/* Upload Area */}
                        <div
                          onClick={() => fileInputRef.current?.click()}
                          className="border border-dashed border-white/20 rounded-xl p-4 text-center hover:bg-white/5 cursor-pointer transition-colors group/upload"
                        >
                          <Upload className="w-6 h-6 mx-auto mb-2 text-muted-foreground group-hover/upload:text-primary transition-colors" />
                          <p className="text-xs font-medium">Click to Upload</p>
                          <p className="text-[10px] text-muted-foreground">PDFs, Docs, Images</p>
                        </div>

                        {/* RAG Toggle */}
                        <div className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                          <div className="space-y-0.5">
                            <span className="text-xs font-medium flex items-center gap-2">
                              <FileText className="w-3 h-3 text-amber-500" />
                              RAG (Documents)
                            </span>
                            <p className="text-[10px] text-muted-foreground">Chat with files</p>
                          </div>
                          <Switch checked={useRag} onCheckedChange={setUseRag} className="scale-75" />
                        </div>
                      </div>
                    </PopoverContent>
                  </Popover>
                  <TooltipContent side="top" className="bg-black/90 border-white/10 backdrop-blur-md text-white">
                    <p>Upload & Documents</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                multiple
                onChange={handleFileUpload}
                accept=".pdf,.txt,.docx,.md,.jpg,.jpeg,.png,.gif,.webp"
              />
            </div>

            {/* Input Area */}
            <div className="relative flex-1">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything..."
                className="min-h-[44px] w-full resize-none border-0 bg-transparent py-3 px-2 focus-visible:ring-0 text-base placeholder:text-muted-foreground/50 shadow-none scrollbar-none"
                rows={1}
              />
            </div>

            {/* Right Actions: Just Send Button */}
            <div className="flex items-center gap-2 pb-1">
              <Button
                onClick={handleSubmit}
                className={`
                  h-10 w-10 rounded-full transition-all duration-300 shadow-lg
                  ${(input.trim() || attachments.length > 0)
                    ? 'bg-gradient-to-br from-primary to-accent text-primary-foreground hover:scale-105 hover:shadow-xl hover:shadow-primary/20'
                    : 'bg-muted text-muted-foreground'
                  }
                `}
                disabled={(!input.trim() && attachments.length === 0) || isTyping}
              >
                {isTyping ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5 ml-0.5" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <p className="text-[10px] text-center text-muted-foreground/50 mt-4 select-none">
        AI will make mistakes. Check important info.
      </p>
    </div>
  );
};
