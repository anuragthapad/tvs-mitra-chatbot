-- Create loan_applications table
CREATE TABLE IF NOT EXISTS loan_applications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT NOT NULL,
  age INTEGER NOT NULL,
  annual_salary NUMERIC NOT NULL,
  pincode TEXT NOT NULL,
  qualification TEXT NOT NULL,
  employment_type TEXT NOT NULL,
  make_code TEXT NOT NULL,
  past_loans TEXT NOT NULL,
  loan_amount NUMERIC NOT NULL,
  
  -- Derived features
  monthly_salary NUMERIC NOT NULL,
  ltv_ratio NUMERIC NOT NULL,
  age_bin TEXT NOT NULL,
  salary_bin TEXT NOT NULL,
  ltv_bin TEXT NOT NULL,
  state TEXT NOT NULL,
  state_avg_salary NUMERIC,
  final_tier TEXT,
  avg_model_price NUMERIC,
  employment_age_interaction TEXT NOT NULL,
  qualification_employment_interaction TEXT NOT NULL,
  salary_ltv_ratio NUMERIC NOT NULL,
  age_salary_ratio NUMERIC NOT NULL,
  
  -- Prediction results
  approval_probability NUMERIC NOT NULL,
  is_approved BOOLEAN NOT NULL,
  recommended_models TEXT[] NOT NULL,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create customer_feedback table
CREATE TABLE IF NOT EXISTS customer_feedback (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  loan_application_id UUID NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
  ease_of_use_rating INTEGER NOT NULL CHECK (ease_of_use_rating >= 1 AND ease_of_use_rating <= 5),
  model_satisfaction_rating INTEGER NOT NULL CHECK (model_satisfaction_rating >= 1 AND model_satisfaction_rating <= 5),
  overall_satisfaction_rating INTEGER NOT NULL CHECK (overall_satisfaction_rating >= 1 AND overall_satisfaction_rating <= 5),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create model_evaluation_metrics table
CREATE TABLE IF NOT EXISTS model_evaluation_metrics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  accuracy NUMERIC NOT NULL,
  precision_score NUMERIC NOT NULL,
  recall NUMERIC NOT NULL,
  f1_score NUMERIC NOT NULL,
  roc_auc NUMERIC NOT NULL,
  gini_coefficient NUMERIC NOT NULL,
  model_version TEXT NOT NULL,
  training_data_size INTEGER NOT NULL,
  feature_count INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disable RLS for public access (since this is a public chatbot)
ALTER TABLE loan_applications DISABLE ROW LEVEL SECURITY;
ALTER TABLE customer_feedback DISABLE ROW LEVEL SECURITY;
ALTER TABLE model_evaluation_metrics DISABLE ROW LEVEL SECURITY;

-- Grant permissions for anonymous access
GRANT ALL ON loan_applications TO anon;
GRANT ALL ON customer_feedback TO anon;
GRANT ALL ON model_evaluation_metrics TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;
