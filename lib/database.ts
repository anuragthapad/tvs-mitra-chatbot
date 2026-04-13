import { createClient } from "@/lib/supabase/client"

export interface UserSession {
  id?: string
  session_id: string
  start_time?: string
  end_time?: string
  total_time_spent_seconds?: number
  device_info?: string
  is_completed: boolean
  created_at?: string
  updated_at?: string
}

export interface LoanApplicationData {
  session_id: string
  // User Input Fields
  age: number
  pincode: string
  annual_salary: number
  monthly_salary: number
  qualification: string
  employment_type: string
  make_code: string
  past_loans?: string
  // Feature Engineered Fields
  age_bin?: string
  salary_bin?: string
  ltv_ratio?: number
  state?: string
  state_avg_salary?: number
  final_tier?: string
  avg_model_price?: number
  salary_ltv_ratio?: number
  net_salary?: number
  income_to_loan_ratio?: number
  age_salary_interaction?: number
  employment_age?: string
  // Prediction Results
  prediction_probability?: number
  roc_auc_score?: number
  is_approved: boolean
  recommended_variants?: any
}

export interface CustomerFeedbackData {
  session_id: string
  overall_satisfaction_rating: number
  improvement_areas: string[]
}

export interface ModelEvaluationData {
  session_id: string
  accuracy: number
  precision_score: number
  recall: number
  f1_score: number
  roc_auc: number
  gini_coefficient: number
}

export interface ModelPredictionData {
  session_id: string
  loan_application_id?: string
  input_features: Record<string, any>
  prediction_score: number
  prediction_class: boolean
  confidence_level: number
  model_version?: string
}

export class DatabaseService {
  private supabase: ReturnType<typeof createClient> | null = null
  private isConnected = false

  private getSupabase() {
    if (!this.supabase) {
      try {
        this.supabase = createClient()
      } catch (error) {
        console.error("[v0] Failed to create Supabase client:", error)
        return null
      }
    }
    return this.supabase
  }

  async createUserSession(sessionData: Omit<UserSession, "id" | "created_at" | "updated_at">): Promise<string | null> {
    const supabase = this.getSupabase()
    if (!supabase) {
      console.log("[v0] Supabase not available, using local session")
      return sessionData.session_id
    }

    try {
      const { data, error } = await supabase
        .from("user_sessions")
        .insert({
          ...sessionData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
        .select("session_id")
        .single()

      if (error) {
        console.log("[v0] Database insert error (non-blocking):", error.message)
        return sessionData.session_id
      }

      this.isConnected = true
      console.log("[v0] User session created in database")
      return data.session_id
    } catch (error) {
      console.log("[v0] Network error (non-blocking), continuing with local session")
      return sessionData.session_id
    }
  }

  async updateUserSession(sessionId: string, updates: Partial<UserSession>): Promise<boolean> {
    const supabase = this.getSupabase()
    if (!supabase) return true

    try {
      const { error } = await supabase
        .from("user_sessions")
        .update({
          ...updates,
          updated_at: new Date().toISOString(),
        })
        .eq("session_id", sessionId)

      if (error) {
        console.log("[v0] Session update error (non-blocking):", error.message)
      }
      return true
    } catch (error) {
      console.log("[v0] Network error updating session (non-blocking)")
      return true
    }
  }

  async saveLoanApplication(applicationData: LoanApplicationData): Promise<string | null> {
    const supabase = this.getSupabase()
    if (!supabase) {
      console.log("[v0] Supabase not available, skipping loan application save")
      return "local-" + Date.now()
    }

    try {
      const { data, error } = await supabase
        .from("loan_applications")
        .insert(applicationData)
        .select("id")
        .single()

      if (error) {
        console.log("[v0] Loan application save error (non-blocking):", error.message)
        return "local-" + Date.now()
      }

      console.log("[v0] Loan application saved to database")
      return data.id
    } catch (error) {
      console.log("[v0] Network error saving loan application (non-blocking)")
      return "local-" + Date.now()
    }
  }

  async saveCustomerFeedback(feedbackData: CustomerFeedbackData): Promise<boolean> {
    const supabase = this.getSupabase()
    if (!supabase) {
      console.log("[v0] Supabase not available, skipping feedback save")
      return true
    }

    try {
      const { error } = await supabase.from("customer_feedback").insert(feedbackData)

      if (error) {
        console.log("[v0] Feedback save error (non-blocking):", error.message)
      } else {
        console.log("[v0] Customer feedback saved to database")
      }
      return true
    } catch (error) {
      console.log("[v0] Network error saving feedback (non-blocking)")
      return true
    }
  }

  async saveModelEvaluation(evaluationData: ModelEvaluationData): Promise<boolean> {
    const supabase = this.getSupabase()
    if (!supabase) {
      console.log("[v0] Supabase not available, skipping evaluation save")
      return true
    }

    try {
      const { error } = await supabase.from("model_evaluation_metrics").insert(evaluationData)

      if (error) {
        console.log("[v0] Evaluation save error (non-blocking):", error.message)
      } else {
        console.log("[v0] Model evaluation saved to database")
      }
      return true
    } catch (error) {
      console.log("[v0] Network error saving evaluation (non-blocking)")
      return true
    }
  }

  async saveModelPrediction(predictionData: ModelPredictionData): Promise<string | null> {
    const supabase = this.getSupabase()
    if (!supabase) {
      console.log("[v0] Supabase not available, skipping prediction save")
      return null
    }

    try {
      const { data, error } = await supabase
        .from("model_predictions")
        .insert({
          ...predictionData,
          model_version: predictionData.model_version || "v1.0",
        })
        .select("id")
        .single()

      if (error) {
        console.log("[v0] Prediction save error (non-blocking):", error.message)
        return null
      }

      console.log("[v0] Model prediction saved to database")
      return data.id
    } catch (error) {
      console.log("[v0] Network error saving prediction (non-blocking)")
      return null
    }
  }

  async getSessionAnalytics(sessionId: string): Promise<any> {
    const supabase = this.getSupabase()
    if (!supabase) return null

    try {
      const [session, application, feedback, metrics] = await Promise.all([
        supabase.from("user_sessions").select("*").eq("session_id", sessionId).single(),
        supabase.from("loan_applications").select("*").eq("session_id", sessionId).single(),
        supabase.from("customer_feedback").select("*").eq("session_id", sessionId).single(),
        supabase.from("model_evaluation_metrics").select("*").eq("session_id", sessionId).single(),
      ])

      return {
        session: session.data,
        application: application.data,
        feedback: feedback.data,
        metrics: metrics.data,
      }
    } catch (error) {
      console.log("[v0] Error fetching session analytics:", error)
      return null
    }
  }
}

export const databaseService = new DatabaseService()
