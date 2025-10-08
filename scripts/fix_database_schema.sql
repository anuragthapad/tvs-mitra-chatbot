-- Fix database schema to match application requirements

-- Add missing columns to loan_applications table
ALTER TABLE public.loan_applications 
ADD COLUMN IF NOT EXISTS time_spent_seconds integer,
ADD COLUMN IF NOT EXISTS question_start_time timestamp with time zone,
ADD COLUMN IF NOT EXISTS question_end_time timestamp with time zone;

-- Add missing columns to customer_feedback table
ALTER TABLE public.customer_feedback 
ADD COLUMN IF NOT EXISTS loan_application_id uuid,
ADD COLUMN IF NOT EXISTS ease_of_use_rating integer,
ADD COLUMN IF NOT EXISTS model_satisfaction_rating integer,
ADD COLUMN IF NOT EXISTS additional_comments text,
ADD COLUMN IF NOT EXISTS time_spent_on_feedback integer;

-- Add foreign key constraint for customer_feedback
ALTER TABLE public.customer_feedback 
ADD CONSTRAINT fk_customer_feedback_loan_application 
FOREIGN KEY (loan_application_id) REFERENCES public.loan_applications(id);

-- Add foreign key constraint for loan_applications to user_sessions
ALTER TABLE public.loan_applications 
ADD CONSTRAINT fk_loan_applications_user_session 
FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id);

-- Add foreign key constraint for model_evaluation_metrics to user_sessions  
ALTER TABLE public.model_evaluation_metrics 
ADD CONSTRAINT fk_model_evaluation_user_session 
FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id);

-- Enable RLS and create policies for public access
ALTER TABLE public.loan_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_evaluation_metrics ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public access (for chatbot)
CREATE POLICY "Allow public access to loan_applications" ON public.loan_applications
FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public access to customer_feedback" ON public.customer_feedback
FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public access to model_evaluation_metrics" ON public.model_evaluation_metrics
FOR ALL USING (true) WITH CHECK (true);
