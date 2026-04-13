-- TVS Mitra Chatbot - Complete Database Setup
-- This script creates all tables needed for storing user inputs, results, and ML model metrics

-- =====================================================
-- 1. USER SESSIONS TABLE
-- Stores session tracking and user journey data
-- =====================================================
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text UNIQUE NOT NULL,
    
    -- Session timing
    start_time timestamp with time zone DEFAULT now(),
    end_time timestamp with time zone,
    total_time_spent integer DEFAULT 0,
    
    -- Session progress
    questions_answered integer DEFAULT 0,
    is_completed boolean DEFAULT false,
    
    -- Device info
    user_agent text,
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Enable RLS for user_sessions
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Create policy for public access
DROP POLICY IF EXISTS "Allow public access to user_sessions" ON public.user_sessions;
CREATE POLICY "Allow public access to user_sessions" ON public.user_sessions
    FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- 2. LOAN APPLICATIONS TABLE
-- Stores all user inputs, engineered features, and prediction results
-- =====================================================
DROP TABLE IF EXISTS public.loan_applications CASCADE;

CREATE TABLE public.loan_applications (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text NOT NULL,
    
    -- User input fields
    age integer NOT NULL,
    pincode text NOT NULL,
    qualification text NOT NULL,
    employment_type text NOT NULL,
    make_code text NOT NULL,
    past_loans text,
    annual_salary numeric NOT NULL,
    loan_amount numeric NOT NULL,
    
    -- Feature engineered fields
    monthly_salary numeric,
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
    is_approved boolean DEFAULT false,
    recommended_models jsonb,
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    -- Foreign key to user_sessions
    CONSTRAINT fk_loan_applications_session 
        FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id)
        ON DELETE CASCADE
);

-- Enable RLS for loan_applications
ALTER TABLE public.loan_applications ENABLE ROW LEVEL SECURITY;

-- Create policy for public access
CREATE POLICY "Allow public access to loan_applications" ON public.loan_applications
    FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- 3. CUSTOMER FEEDBACK TABLE
-- Stores user satisfaction ratings and improvement suggestions
-- =====================================================
DROP TABLE IF EXISTS public.customer_feedback CASCADE;

CREATE TABLE public.customer_feedback (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text NOT NULL,
    
    -- Feedback ratings
    overall_satisfaction_rating integer CHECK (overall_satisfaction_rating >= 1 AND overall_satisfaction_rating <= 5),
    
    -- Improvement areas (stored as array)
    improvement_areas text[],
    
    -- Additional feedback
    comments text,
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    
    -- Foreign key to user_sessions
    CONSTRAINT fk_customer_feedback_session 
        FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id)
        ON DELETE CASCADE
);

-- Enable RLS for customer_feedback
ALTER TABLE public.customer_feedback ENABLE ROW LEVEL SECURITY;

-- Create policy for public access
CREATE POLICY "Allow public access to customer_feedback" ON public.customer_feedback
    FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- 4. MODEL EVALUATION METRICS TABLE
-- Stores ML model performance metrics and feature importance
-- =====================================================
DROP TABLE IF EXISTS public.model_evaluation_metrics CASCADE;

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
        ON DELETE CASCADE
);

-- Enable RLS for model_evaluation_metrics
ALTER TABLE public.model_evaluation_metrics ENABLE ROW LEVEL SECURITY;

-- Create policy for public access
CREATE POLICY "Allow public access to model_evaluation_metrics" ON public.model_evaluation_metrics
    FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- 5. MODEL PREDICTIONS HISTORY TABLE
-- Stores individual prediction details for analysis
-- =====================================================
DROP TABLE IF EXISTS public.model_predictions CASCADE;

CREATE TABLE public.model_predictions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id text NOT NULL,
    loan_application_id uuid,
    
    -- Input features used for prediction
    input_features jsonb NOT NULL,
    
    -- Prediction results
    prediction_score numeric,
    prediction_class boolean,
    confidence_level numeric,
    
    -- Model info
    model_version text DEFAULT '1.0',
    
    -- Timestamps
    created_at timestamp with time zone DEFAULT now(),
    
    -- Foreign keys
    CONSTRAINT fk_model_predictions_session 
        FOREIGN KEY (session_id) REFERENCES public.user_sessions(session_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_model_predictions_loan_application 
        FOREIGN KEY (loan_application_id) REFERENCES public.loan_applications(id)
        ON DELETE SET NULL
);

-- Enable RLS for model_predictions
ALTER TABLE public.model_predictions ENABLE ROW LEVEL SECURITY;

-- Create policy for public access
CREATE POLICY "Allow public access to model_predictions" ON public.model_predictions
    FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- 6. INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON public.user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_created_at ON public.user_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_loan_applications_session_id ON public.loan_applications(session_id);
CREATE INDEX IF NOT EXISTS idx_loan_applications_created_at ON public.loan_applications(created_at);
CREATE INDEX IF NOT EXISTS idx_loan_applications_is_approved ON public.loan_applications(is_approved);
CREATE INDEX IF NOT EXISTS idx_customer_feedback_session_id ON public.customer_feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_customer_feedback_rating ON public.customer_feedback(overall_satisfaction_rating);
CREATE INDEX IF NOT EXISTS idx_model_evaluation_metrics_session_id ON public.model_evaluation_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_model_evaluation_metrics_roc_auc ON public.model_evaluation_metrics(roc_auc);
CREATE INDEX IF NOT EXISTS idx_model_predictions_session_id ON public.model_predictions(session_id);
CREATE INDEX IF NOT EXISTS idx_model_predictions_loan_application_id ON public.model_predictions(loan_application_id);

-- =====================================================
-- 7. UPDATED_AT TRIGGER FUNCTION
-- Automatically updates the updated_at timestamp
-- =====================================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
DROP TRIGGER IF EXISTS update_user_sessions_updated_at ON public.user_sessions;
CREATE TRIGGER update_user_sessions_updated_at
    BEFORE UPDATE ON public.user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_loan_applications_updated_at ON public.loan_applications;
CREATE TRIGGER update_loan_applications_updated_at
    BEFORE UPDATE ON public.loan_applications
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();
