import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';

export const AnimatedBackground: React.FC = () => {
    const { theme } = useTheme();

    // Different gradients for each theme
    const gradients = {
        dark: 'from-blue-900/40 via-purple-900/40 to-pink-900/40',
        light: 'from-blue-300 via-purple-300 to-pink-300',
        benz: 'from-yellow-600/20 via-orange-800/20 to-amber-900/40'
    };

    return (
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
            {/* Animated gradient mesh */}
            <div className={`absolute inset-0 bg-gradient-to-br ${gradients[theme]} animate-gradient`} />

            {/* Floating orbs */}
            <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/20 rounded-full blur-[100px] animate-float" />
            <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-secondary/20 rounded-full blur-[100px] animate-float-delayed" />
            <div className="absolute top-1/2 right-1/3 w-96 h-96 bg-accent/20 rounded-full blur-[80px] animate-pulse-slow" />

            {/* Grid overlay */}
            <div className="absolute inset-0 bg-grid-pattern opacity-[0.02]" />
        </div>
    );
};
