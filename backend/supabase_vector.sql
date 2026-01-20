-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your documents
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  content text, -- corresponds to Document.pageContent
  metadata jsonb, -- corresponds to Document.metadata
  embedding vector(384), -- 384 dimensions for all-MiniLM-L6-v2
  conversation_id uuid, -- link to conversation
  created_at timestamp with time zone default now()
);

-- Associate conversation_id with the documents table for easier cleanup/management
-- (Optional: add foreign key if conversations table exists and you want strict integrity)
-- alter table documents add constraint fk_conversation foreign key (conversation_id) references conversations(id) on delete cascade;

-- Create a function to search for documents
create or replace function match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter jsonb default '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  embedding vector(384),
  similarity float
) language plpgsql stable as $$
begin
  return query
  select
    documents.id,
    documents.content,
    documents.metadata,
    documents.embedding,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  and metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;
