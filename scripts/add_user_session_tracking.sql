-- Add user session tracking table
CREATE TABLE IF NOT EXISTS public.user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  total_time_spent INTEGER DEFAULT 0, -- in seconds
  questions_answered INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  user_agent TEXT,
  ip_address INET
);

-- Add time tracking columns to existing tables
ALTER TABLE public.loan_applications 
ADD COLUMN IF NOT EXISTS time_spent_seconds INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS question_start_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS question_end_time TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.customer_feedback 
ADD COLUMN IF NOT EXISTS time_spent_on_feedback INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS improvement_areas TEXT[];

-- Enable RLS for public access (no authentication required)
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public access to user_sessions" ON public.user_sessions FOR ALL USING (true);

-- Update existing RLS policies for public access
DROP POLICY IF EXISTS "Allow public access to loan_applications" ON public.loan_applications;
CREATE POLICY "Allow public access to loan_applications" ON public.loan_applications FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow public access to customer_feedback" ON public.customer_feedback;
CREATE POLICY "Allow public access to customer_feedback" ON public.customer_feedback FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow public access to model_evaluation_metrics" ON public.model_evaluation_metrics;
CREATE POLICY "Allow public access to model_evaluation_metrics" ON public.model_evaluation_metrics FOR ALL USING (true);
