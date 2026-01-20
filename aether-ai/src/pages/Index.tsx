import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { ChatProvider } from '@/contexts/ChatContext';
import { WelcomeScreen } from '@/components/welcome/WelcomeScreen';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { AnimatedBackground } from '@/components/AnimatedBackground';

const Index: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <>
        <AnimatedBackground />
        <WelcomeScreen />
      </>
    );
  }

  return (
    <ChatProvider>
      <AnimatedBackground />
      <ChatInterface />
    </ChatProvider>
  );
};

export default Index;
