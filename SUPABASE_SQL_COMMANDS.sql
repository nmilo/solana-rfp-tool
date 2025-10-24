-- 🚀 Supabase SQL Setup Commands
-- Run these in: https://supabase.com/dashboard/project/zaqonwxzoafewoloexsk/sql

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create knowledge_base table with embedding column
-- Using text-embedding-3-large (3072 dimensions) for best accuracy
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(255),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    confidence_threshold FLOAT DEFAULT 0.1,
    embedding TEXT  -- Stored as JSON text, 3072 dimensions for text-embedding-3-large
);

-- Create question_submissions table
CREATE TABLE IF NOT EXISTS question_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id VARCHAR(255) UNIQUE NOT NULL,
    questions JSONB NOT NULL,
    answers JSONB,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_knowledge_base_question 
ON knowledge_base USING gin(to_tsvector('english', question));

CREATE INDEX IF NOT EXISTS idx_knowledge_base_category 
ON knowledge_base(category);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags 
ON knowledge_base USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_active 
ON knowledge_base(is_active);

-- Add sample data
INSERT INTO users (email, name, is_active)
VALUES ('demo@solana.org', 'Demo User', true)
ON CONFLICT (email) DO NOTHING;

INSERT INTO knowledge_base (question, answer, category, tags, is_active)
VALUES (
    'What is Solana?',
    'Solana is a high-performance blockchain platform designed for decentralized applications and crypto-currencies. It uses a unique Proof of History consensus mechanism to achieve fast transaction speeds and low costs.',
    'General',
    '["solana", "blockchain", "consensus"]',
    true
)
ON CONFLICT DO NOTHING;

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_submissions ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (for demo purposes)
CREATE POLICY "Allow public read access to knowledge_base" ON knowledge_base
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to knowledge_base" ON knowledge_base
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update access to knowledge_base" ON knowledge_base
    FOR UPDATE USING (true);

CREATE POLICY "Allow public read access to users" ON users
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to users" ON users
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to question_submissions" ON question_submissions
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to question_submissions" ON question_submissions
    FOR INSERT WITH CHECK (true);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
