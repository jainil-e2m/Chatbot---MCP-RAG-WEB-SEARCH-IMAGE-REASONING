import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { LoginForm } from '@/components/auth/LoginForm';
import { SignupForm } from '@/components/auth/SignupForm';
import { Brain, Search, FileText, ArrowRight } from 'lucide-react';

export const WelcomeScreen: React.FC = () => {
  const [showAuth, setShowAuth] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-accent/30" />

      {/* Floating orbs for visual interest */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-secondary/5 rounded-full blur-3xl animate-pulse delay-1000" />

      <div className="relative z-10 flex flex-col items-center px-6 text-center max-w-2xl mx-auto">
        {/* Logo/Brand */}
        <div className="mb-8 flex flex-col items-center gap-6">
          <div className="w-36 h-36 rounded-3xl overflow-hidden bg-primary flex items-center justify-center shadow-2xl ring-4 ring-primary/20">
            <img src="/logo2.png" alt="TrustMeBro! AI" className="w-full h-full object-cover" />
          </div>
          <h1 className="text-5xl font-semibold text-foreground tracking-tight">TrustMeBro! AI</h1>
        </div>

        {/* Tagline with Hover Effect */}
        <div
          className="relative min-h-[120px] flex items-center justify-center mb-6 cursor-help"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <AnimatePresence mode="wait">
            {isHovered ? (
              <motion.h2
                key="risk"
                initial={{ opacity: 0, scale: 0.95, filter: 'blur(5px)' }}
                animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                exit={{ opacity: 0, scale: 1.05, filter: 'blur(5px)' }}
                transition={{ duration: 0.3 }}
                className="text-4xl md:text-5xl font-serif font-bold text-red-500 leading-tight uppercase tracking-widest"
              >
                IT MAY/MAY NOT WORK.<br />USE AT YOUR OWN RISK.
              </motion.h2>
            ) : (
              <motion.h2
                key="tagline"
                initial={{ opacity: 0, scale: 0.95, filter: 'blur(5px)' }}
                animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                exit={{ opacity: 0, scale: 1.05, filter: 'blur(5px)' }}
                transition={{ duration: 0.3 }}
                className="text-4xl md:text-5xl font-serif font-medium text-foreground leading-tight"
              >
                Your intelligent workspace for research, reasoning, and creation.
              </motion.h2>
            )}
          </AnimatePresence>
        </div>

        {/* Description */}
        <p className="text-lg text-muted-foreground mb-12 max-w-xl leading-relaxed">
          Talk to powerful AI models, use advanced tools, search the web, and work with your documents — all in one unified AI workspace.
        </p>

        {!showAuth ? (
          <div className="space-y-6">
            <Button
              onClick={() => {
                setShowAuth(true);
                setIsSignup(false);
              }}
              size="lg"
              className="h-14 px-8 text-lg font-medium transition-all duration-300 hover:scale-[1.02] group"
            >
              Log in to continue
              <ArrowRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
            </Button>

            <p className="text-sm text-muted-foreground">
              New user?{' '}
              <button
                onClick={() => {
                  setShowAuth(true);
                  setIsSignup(true);
                }}
                className="text-primary hover:underline transition-colors font-medium"
              >
                Sign up
              </button>
            </p>
          </div>
        ) : (
          <div className="w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
            {isSignup ? (
              <SignupForm onSwitchToLogin={() => setIsSignup(false)} />
            ) : (
              <LoginForm onSwitchToSignup={() => setIsSignup(true)} />
            )}
            <button
              onClick={() => setShowAuth(false)}
              className="mt-6 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Back to welcome
            </button>
          </div>
        )}

        {/* Feature highlights */}
        {!showAuth && (
          <div className="mt-20 grid grid-cols-3 gap-8 text-left animate-in fade-in slide-in-from-bottom-6 duration-700 delay-200">
            <FeatureCard
              icon={<Brain className="w-5 h-5" />}
              title="Multiple Models"
              description="GPT-4, Gemini, Mistral, and more"
            />
            <FeatureCard
              icon={<Search className="w-5 h-5" />}
              title="Web Search"
              description="Real-time information retrieval"
            />
            <FeatureCard
              icon={<FileText className="w-5 h-5" />}
              title="Document RAG"
              description="Chat with your documents"
            />
          </div>
        )}
      </div>
    </div>
  );
};

const FeatureCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string
}> = ({ icon, title, description }) => (
  <div className="flex flex-col items-start gap-2 p-4 rounded-lg bg-card/50 border border-border/30">
    <div className="p-2 rounded-md bg-primary/10 text-primary">
      {icon}
    </div>
    <h3 className="font-medium text-foreground">{title}</h3>
    <p className="text-sm text-muted-foreground">{description}</p>
  </div>
);
