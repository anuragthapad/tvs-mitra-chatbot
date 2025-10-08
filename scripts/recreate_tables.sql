-- Drop and recreate all tables except user_sessions to fix data loading issues
-- Drop existing tables (except user_sessions)
DROP TABLE IF EXISTS public.customer_feedback CASCADE;
DROP TABLE IF EXISTS public.loan_applications CASCADE;
DROP TABLE IF EXISTS public.model_evaluation_metrics CASCADE;

-- Recreate loan_applications table with proper structure
CREATE TABLE public.loan_applications (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text NOT NULL,
    
    -- User input fields
    age integer NOT NULL,
    pincode text NOT NULL,
    qualification text NOT NULL,
    employment_type text NOT NULL,
    make_code text NOT NULL,
    past_loans text NOT NULL,
    annual_salary numeric NOT NULL,
    loan_amount numeric NOT NULL,
    
    -- Feature engineered fields
    monthly_salary numeric NOT NULL,
    state text,
    state_avg_salary numeric,
    avg_model_price numeric,
    ltv_ratio numeric,
    salary_ltv_ratio numeric,
    age_salary_ratio numeric,
    employment_age_interaction text,
    qualification_employment_interaction text,
    age_bin text,
    salary_bin text,
    ltv_bin text,
    final_tier text,
    
    -- Model evaluation results
    approval_probability numeric,
    is_approved boolean,
    recommended_models jsonb,
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    -- Foreign key to user_sessions
    CONSTRAINT fk_loan_applications_session 
        FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id)
);

-- Recreate customer_feedback table
CREATE TABLE public.customer_feedback (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text NOT NULL,
    
    -- Feedback ratings
    overall_satisfaction_rating integer CHECK (overall_satisfaction_rating >= 1 AND overall_satisfaction_rating <= 5),
    
    -- Improvement areas (stored as array)
    improvement_areas text[],
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    
    -- Foreign key to user_sessions
    CONSTRAINT fk_customer_feedback_session 
        FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id)
);

-- Recreate model_evaluation_metrics table
CREATE TABLE public.model_evaluation_metrics (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text NOT NULL,
    
    -- Model performance metrics
    accuracy numeric,
    precision_score numeric,
    recall numeric,
    f1_score numeric,
    roc_auc numeric,
    gini_coefficient numeric,
    
    -- Model metadata
    model_version text DEFAULT '1.0',
    feature_count integer,
    training_data_size integer,
    feature_importance jsonb,
    model_parameters jsonb,
    training_date timestamp with time zone DEFAULT now(),
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    
    -- Foreign key to user_sessions
    CONSTRAINT fk_model_evaluation_metrics_session 
        FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id)
);

-- Enable Row Level Security (RLS) for public access
ALTER TABLE public.loan_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_evaluation_metrics ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (no authentication required)
CREATE POLICY "Allow public access to loan_applications" ON public.loan_applications
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public access to customer_feedback" ON public.customer_feedback
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public access to model_evaluation_metrics" ON public.model_evaluation_metrics
    FOR ALL USING (true) WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX idx_loan_applications_session_id ON public.loan_applications(session_id);
CREATE INDEX idx_customer_feedback_session_id ON public.customer_feedback(session_id);
CREATE INDEX idx_model_evaluation_metrics_session_id ON public.model_evaluation_metrics(session_id);
CREATE INDEX idx_loan_applications_created_at ON public.loan_applications(created_at);
