-- TVS Mitra Chatbot Database Schema
-- This script creates all required tables for the loan application chatbot

-- Drop existing tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS model_evaluation_metrics CASCADE;
DROP TABLE IF EXISTS customer_feedback CASCADE;
DROP TABLE IF EXISTS loan_applications CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;

-- 1. User Sessions Table - Tracks user interactions and time spent
CREATE TABLE user_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    total_time_spent_seconds INTEGER DEFAULT 0,
    device_info TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Loan Applications Table - Stores user inputs and feature engineered values
CREATE TABLE loan_applications (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    
    -- User Input Fields
    age INTEGER NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    annual_salary DECIMAL(15,2) NOT NULL,
    monthly_salary DECIMAL(15,2) NOT NULL,
    qualification VARCHAR(50) NOT NULL,
    employment_type VARCHAR(50) NOT NULL,
    make_code VARCHAR(100) NOT NULL,
    past_loans VARCHAR(50),
    
    -- Feature Engineered Fields
    age_bin VARCHAR(50),
    salary_bin VARCHAR(50),
    ltv_ratio DECIMAL(10,4),
    state VARCHAR(100),
    state_avg_salary DECIMAL(15,2),
    final_tier VARCHAR(50),
    avg_model_price DECIMAL(15,2),
    salary_ltv_ratio DECIMAL(10,4),
    net_salary DECIMAL(15,2),
    income_to_loan_ratio DECIMAL(10,4),
    age_salary_interaction DECIMAL(15,2),
    employment_age VARCHAR(100),
    
    -- Prediction Results
    prediction_probability DECIMAL(10,6),
    roc_auc_score DECIMAL(10,6),
    is_approved BOOLEAN DEFAULT FALSE,
    recommended_variants JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Customer Feedback Table - Stores user feedback after prediction
CREATE TABLE customer_feedback (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    
    -- Feedback Fields
    overall_satisfaction_rating INTEGER CHECK (overall_satisfaction_rating >= 1 AND overall_satisfaction_rating <= 5),
    improvement_areas TEXT[],
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Model Evaluation Metrics Table - Stores model performance metrics
CREATE TABLE model_evaluation_metrics (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    
    -- Model Metrics
    accuracy DECIMAL(10,6),
    precision_score DECIMAL(10,6),
    recall DECIMAL(10,6),
    f1_score DECIMAL(10,6),
    roc_auc DECIMAL(10,6),
    gini_coefficient DECIMAL(10,6),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX idx_loan_applications_session_id ON loan_applications(session_id);
CREATE INDEX idx_customer_feedback_session_id ON customer_feedback(session_id);
CREATE INDEX idx_model_evaluation_session_id ON model_evaluation_metrics(session_id);
CREATE INDEX idx_loan_applications_created_at ON loan_applications(created_at);

-- Disable Row Level Security for public access (no auth required)
ALTER TABLE user_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE loan_applications DISABLE ROW LEVEL SECURITY;
ALTER TABLE customer_feedback DISABLE ROW LEVEL SECURITY;
ALTER TABLE model_evaluation_metrics DISABLE ROW LEVEL SECURITY;

-- Grant public access
GRANT ALL ON user_sessions TO anon, authenticated;
GRANT ALL ON loan_applications TO anon, authenticated;
GRANT ALL ON customer_feedback TO anon, authenticated;
GRANT ALL ON model_evaluation_metrics TO anon, authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
