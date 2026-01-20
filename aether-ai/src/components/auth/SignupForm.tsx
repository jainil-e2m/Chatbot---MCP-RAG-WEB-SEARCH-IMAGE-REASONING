import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';

interface SignupFormProps {
    onSwitchToLogin?: () => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSwitchToLogin }) => {
    const { signup, isLoading, error, clearError } = useAuth();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [localError, setLocalError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLocalError(null);

        // Client-side validation
        if (password !== confirmPassword) {
            setLocalError('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            setLocalError('Password must be at least 6 characters long');
            return;
        }

        await signup(name, email, password, confirmPassword);
    };

    const displayError = localError || error;

    return (
        <form onSubmit={handleSubmit} className="space-y-6 w-full max-w-sm">
            <div className="space-y-2">
                <Label htmlFor="name" className="text-foreground/80">Name</Label>
                <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    value={name}
                    onChange={(e) => {
                        setName(e.target.value);
                        if (displayError) {
                            clearError();
                            setLocalError(null);
                        }
                    }}
                    required
                    className="h-12 bg-card border-border/50 focus:border-primary transition-colors"
                />
            </div>
            <div className="space-y-2">
                <Label htmlFor="email" className="text-foreground/80">Email</Label>
                <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => {
                        setEmail(e.target.value);
                        if (displayError) {
                            clearError();
                            setLocalError(null);
                        }
                    }}
                    required
                    className="h-12 bg-card border-border/50 focus:border-primary transition-colors"
                />
            </div>
            <div className="space-y-2">
                <Label htmlFor="password" className="text-foreground/80">Password</Label>
                <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => {
                        setPassword(e.target.value);
                        if (displayError) {
                            clearError();
                            setLocalError(null);
                        }
                    }}
                    required
                    className="h-12 bg-card border-border/50 focus:border-primary transition-colors"
                />
            </div>
            <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-foreground/80">Confirm Password</Label>
                <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        if (displayError) {
                            clearError();
                            setLocalError(null);
                        }
                    }}
                    required
                    className="h-12 bg-card border-border/50 focus:border-primary transition-colors"
                />
            </div>
            {displayError && (
                <p className="text-sm text-destructive animate-in fade-in">{displayError}</p>
            )}
            <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-base font-medium transition-all duration-200 hover:scale-[1.02]"
            >
                {isLoading ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating account...
                    </>
                ) : (
                    'Sign up'
                )}
            </Button>
            {onSwitchToLogin && (
                <p className="text-center text-sm text-muted-foreground">
                    Already have an account?{' '}
                    <button
                        type="button"
                        onClick={onSwitchToLogin}
                        className="text-primary hover:underline font-medium"
                    >
                        Sign in
                    </button>
                </p>
            )}
        </form>
    );
};
