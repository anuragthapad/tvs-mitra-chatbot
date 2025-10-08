-- Create user_sessions table for tracking user interactions
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    total_time_spent INTEGER DEFAULT 0, -- in seconds
    current_question_index INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    user_agent TEXT,
    ip_address INET,
    is_completed BOOLEAN DEFAULT FALSE,
    completion_time TIMESTAMP WITH TIME ZONE
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON public.user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_created_at ON public.user_sessions(created_at);

-- Enable RLS (Row Level Security)
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for now (since this is a public chatbot)
CREATE POLICY "Allow all operations on user_sessions" ON public.user_sessions
    FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions
GRANT ALL ON public.user_sessions TO anon;
GRANT ALL ON public.user_sessions TO authenticated;
