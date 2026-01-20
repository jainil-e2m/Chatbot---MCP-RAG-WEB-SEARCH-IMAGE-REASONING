-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create policies (simplified for now, assumes authenticated user access)
CREATE POLICY "Users can view their own conversations" 
    ON conversations FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own conversations" 
    ON conversations FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view messages in their conversations" 
    ON messages FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM conversations 
            WHERE id = messages.conversation_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages in their conversations" 
    ON messages FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM conversations 
            WHERE id = conversation_id 
            AND user_id = auth.uid()
        )
    );
