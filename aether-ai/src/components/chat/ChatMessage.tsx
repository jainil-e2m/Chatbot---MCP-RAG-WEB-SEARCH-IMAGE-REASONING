import React, { useState } from 'react';
import { motion } from 'framer-motion';
import type { ChatMessage as ChatMessageType } from '@/types';
import { User, Bot, ExternalLink, Copy, Check, Terminal } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Animation variants
  const variants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: { opacity: 1, y: 0, scale: 1 }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to extract text from React children/nodes recursively
  const extractTextFromNode = (node: any): string => {
    if (typeof node === 'string') return node;
    if (Array.isArray(node)) return node.map(extractTextFromNode).join('');
    if (node && node.props && node.props.children) return extractTextFromNode(node.props.children);
    if (node && node.children) {
      return node.children.map((child: any) => {
        if (child.type === 'text') return child.value;
        return extractTextFromNode(child);
      }).join('');
    }
    return '';
  };

  const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : '';
    const codeContent = String(children).replace(/\n$/, '');
    const [isCodeCopied, setIsCodeCopied] = useState(false);

    const handleCopyCode = async () => {
      await navigator.clipboard.writeText(codeContent);
      setIsCodeCopied(true);
      setTimeout(() => setIsCodeCopied(false), 2000);
    };

    if (!inline && match) {
      return (
        <div className="relative my-4 rounded-lg overflow-hidden border border-border/50 bg-[#1e1e1e] shadow-lg group/code">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-border/10 text-xs text-gray-400 select-none">
            <div className="flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5" />
              <span className="font-mono font-medium">{language}</span>
            </div>
            <button
              onClick={handleCopyCode}
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              {isCodeCopied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-green-400" />
                  <span className="text-green-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy code</span>
                </>
              )}
            </button>
          </div>

          {/* Code */}
          <div className="overflow-x-auto">
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={language}
              PreTag="div"
              customStyle={{
                margin: 0,
                padding: '1.5rem',
                background: 'transparent',
                fontSize: '0.875rem',
                lineHeight: '1.6',
              }}
              {...props}
            >
              {codeContent}
            </SyntaxHighlighter>
          </div>
        </div>
      );
    }

    return (
      <code className="bg-muted px-1.5 py-0.5 rounded font-mono text-sm border border-border/50" {...props}>
        {children}
      </code>
    );
  };

  const TableBlock = ({ node, className, children, ...props }: any) => {
    const [isTableCopied, setIsTableCopied] = useState(false);

    const handleCopyTable = () => {
      // Simple extraction strategy: traverse the 'node' AST from remark-gfm
      // Note: 'node' here is the hast node.
      if (!node || !node.children) return;

      let tsv = '';

      // Find thead and tbody
      const thead = node.children.find((c: any) => c.tagName === 'thead');
      const tbody = node.children.find((c: any) => c.tagName === 'tbody');

      const extractRow = (row: any) => {
        return row.children
          .filter((c: any) => c.tagName === 'th' || c.tagName === 'td')
          .map((cell: any) => {
            // Cell children are usually text nodes or elements (like bold)
            // We need a helper to extract text from HAST nodes
            const cellText = cell.children.map((child: any) => {
              if (child.type === 'text') return child.value;
              if (child.tagName === 'strong' || child.tagName === 'em' || child.tagName === 'code' || child.tagName === 'span') {
                // Recursive simplified (assuming mostly text)
                return child.children ? child.children.map((c: any) => c.value || '').join('') : '';
              }
              return '';
            }).join('');
            return cellText.trim();
          })
          .join('\t');
      };

      if (thead) {
        thead.children.forEach((row: any) => {
          if (row.tagName === 'tr') {
            tsv += extractRow(row) + '\n';
          }
        });
      }

      if (tbody) {
        tbody.children.forEach((row: any) => {
          if (row.tagName === 'tr') {
            tsv += extractRow(row) + '\n';
          }
        });
      }

      navigator.clipboard.writeText(tsv);
      setIsTableCopied(true);
      setTimeout(() => setIsTableCopied(false), 2000);
    };

    return (
      <div className="relative my-6 rounded-xl overflow-hidden border border-border/40 shadow-sm bg-card/50 group">
        {/* Table Actions Toolbar (Appears on Hover) */}
        <div className="absolute top-2 right-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
          <button
            onClick={handleCopyTable}
            className="flex items-center gap-1.5 px-2 py-1 bg-background/80 backdrop-blur border border-border/50 rounded-md shadow-sm text-xs font-medium hover:bg-background hover:text-primary transition-all"
            title="Copy as TSV (Excel/Sheets)"
          >
            {isTableCopied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{isTableCopied ? 'Copied' : 'Copy Table'}</span>
          </button>
        </div>

        <div className="overflow-x-auto group p-1">
          <table className="min-w-full w-full border-collapse text-sm" {...props}>
            {children}
          </table>
        </div>
      </div>
    );
  };

  // Custom Table Components for styling
  const TableHeader = ({ node, ...props }: any) => <thead className="bg-muted/50 border-b border-border/50" {...props} />;
  const TableBody = ({ node, ...props }: any) => <tbody className="bg-transparent" {...props} />;
  const TableRow = ({ node, ...props }: any) => <tr className="border-b border-border/20 last:border-0 hover:bg-muted/30 transition-colors" {...props} />;
  const TableHead = ({ node, ...props }: any) => <th className="px-4 py-3 text-left font-semibold text-muted-foreground align-middle" {...props} />;
  const TableCell = ({ node, ...props }: any) => <td className="px-4 py-3 align-middle" {...props} />;



  return (
    <>
      <motion.div
        initial="hidden"
        animate="visible"
        variants={variants}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className={`flex gap-4 mb-4 ${isUser ? 'flex-row-reverse' : ''}`}
      >
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${isUser
          ? 'bg-gradient-to-br from-primary to-accent text-primary-foreground'
          : 'bg-gradient-to-br from-secondary to-muted text-secondary-foreground'
          }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message content */}
        <div className={`flex flex-col max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
          {/* Tools used badge */}
          {message.toolsUsed && message.toolsUsed.length > 0 && (
            <div className="flex gap-1 mb-2 flex-wrap justify-end">
              {message.toolsUsed.map((tool) => (
                <Badge key={tool} variant="outline" className="text-[10px] bg-background/50 backdrop-blur border-primary/20">
                  {tool}
                </Badge>
              ))}
            </div>
          )}

          {/* Message bubble */}
          <div className={`relative group/message rounded-2xl px-5 py-4 shadow-sm backdrop-blur-md border ${isUser
            ? 'bg-gradient-to-br from-primary/90 to-primary/80 text-primary-foreground border-primary/20 rounded-tr-none'
            : 'bg-card/40 text-card-foreground border-white/10 rounded-tl-none'
            }`}>
            {/* Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {message.attachments.map((att, i) => (
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    key={i}
                    className="group relative rounded-xl overflow-hidden border border-border/50 bg-background/10 shadow-sm"
                  >
                    {att.type === 'image' ? (
                      <div className="relative w-48 h-32">
                        <img src={att.url} alt={att.name} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                          <button
                            onClick={() => setPreviewImage(att.url)}
                            className="p-2 bg-background/20 backdrop-blur-md rounded-full hover:bg-background/40 text-white transition-all ring-1 ring-white/20"
                            title="View"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3 p-3 w-48">
                        <div className="p-2 bg-background/20 rounded-lg">
                          <User className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium truncate">{att.name}</p>
                          <p className="text-[10px] opacity-70">Document</p>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}

            {/* Content (Markdown) */}
            <div className={`prose prose-sm max-w-none dark:prose-invert leading-relaxed ${isUser ? 'prose-headings:text-primary-foreground prose-p:text-primary-foreground/90 prose-strong:text-primary-foreground' : ''}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: CodeBlock,
                  table: TableBlock,
                  thead: TableHeader,
                  tbody: TableBody,
                  tr: TableRow,
                  th: TableHead,
                  td: TableCell
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Generated Image Display */}
            {message.imageUrl && (
              <div className="mt-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  className="relative rounded-xl overflow-hidden border border-border/50 bg-background/10 shadow-lg max-w-md"
                >
                  <img
                    src={message.imageUrl}
                    alt="Generated image"
                    className="w-full h-auto cursor-pointer hover:scale-105 transition-transform duration-300"
                    onClick={() => setPreviewImage(message.imageUrl!)}
                  />
                  <div className="absolute top-2 right-2 bg-black/50 backdrop-blur-sm px-2 py-1 rounded-md text-xs text-white">
                    Generated Image
                  </div>
                </motion.div>
              </div>
            )}

            {/* Message Copy Button (Bottom Right) */}
            {!isUser && (
              <div className="absolute -bottom-6 left-0 opacity-0 group-hover/message:opacity-100 transition-opacity duration-200">
                <button
                  onClick={() => copyToClipboard(message.content)}
                  className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground p-1 rounded-md transition-colors"
                >
                  {copied ? (
                    <Check className="w-3.5 h-3.5 text-green-500" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Image Preview Modal */}
      {previewImage && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
          onClick={() => setPreviewImage(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="relative max-w-4xl max-h-[90vh] bg-background rounded-xl overflow-hidden shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setPreviewImage(null)}
              className="absolute top-4 right-4 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <img src={previewImage} alt="Preview" className="w-full h-full object-contain" />
          </motion.div>
        </motion.div>
      )}
    </>
  );
};

// Local Icon imports if missing (X was missing)
import { X } from 'lucide-react';
