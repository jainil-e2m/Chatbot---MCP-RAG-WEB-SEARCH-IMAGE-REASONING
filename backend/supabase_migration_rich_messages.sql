-- Migration: Add rich message metadata columns
-- Run this in Supabase SQL Editor

-- Add columns for image URLs, sources, and tools used
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS image_url TEXT,
ADD COLUMN IF NOT EXISTS sources JSONB,
ADD COLUMN IF NOT EXISTS tools_used JSONB;

-- Add index for faster conversation queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- Add policy for updating conversations (drop if exists first)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'conversations' 
        AND policyname = 'Users can update their own conversations'
    ) THEN
        CREATE POLICY "Users can update their own conversations" 
            ON conversations FOR UPDATE 
            USING (auth.uid() = user_id);
    END IF;
END $$;
