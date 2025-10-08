import { createClient } from "@/lib/supabase/client"

export interface UserSession {
  id?: string
  session_id: string
  created_at?: string
  updated_at?: string
  total_time_spent: number
  questions_answered: number
  is_completed: boolean
  user_agent?: string
  ip_address?: string
}

export interface LoanApplicationData {
  session_id: string
  age: number
  annual_salary: number
  monthly_salary: number
  loan_amount: number
  pincode: string
  qualification: string
  employment_type: string
  make_code: string
  past_loans: string
  ltv_ratio: number
  state: string
  state_avg_salary: number
  avg_model_price: number
  final_tier: string
  age_bin: string
  salary_bin: string
  ltv_bin: string
  employment_age_interaction: string
  qualification_employment_interaction: string
  salary_ltv_ratio: number
  age_salary_ratio: number
  approval_probability: number
  is_approved: boolean
  recommended_models: any[]
}

export interface CustomerFeedbackData {
  session_id: string
  overall_satisfaction_rating: number
  improvement_areas: string[]
}

export interface ModelEvaluationData {
  session_id: string
  model_version: string
  accuracy: number
  precision_score: number
  recall: number
  f1_score: number
  roc_auc: number
  gini_coefficient: number
  training_data_size: number
  feature_count: number
  model_parameters: any
  feature_importance: any
  training_date: string
}

export class DatabaseService {
  private supabase = createClient()

  async createUserSession(sessionData: Omit<UserSession, "id" | "created_at" | "updated_at">): Promise<string | null> {
    try {
      console.log("[v0] Creating user session with data:", sessionData)

      const { data, error } = await this.supabase
        .from("user_sessions")
        .insert({
          ...sessionData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
        .select("session_id")
        .single()

      if (error) {
        console.error("[v0] Supabase error creating user session:", error)
        // Return the session_id from input data as fallback
        return sessionData.session_id
      }

      console.log("[v0] User session created successfully:", data)
      return data.session_id
    } catch (error) {
      console.error("[v0] Database error creating session:", error)
      // Return the session_id from input data as fallback
      return sessionData.session_id
    }
  }

  async updateUserSession(sessionId: string, updates: Partial<UserSession>): Promise<boolean> {
    try {
      console.log("[v0] Updating user session:", sessionId, updates)

      const { error } = await this.supabase
        .from("user_sessions")
        .update({
          ...updates,
          updated_at: new Date().toISOString(),
        })
        .eq("session_id", sessionId)

      if (error) {
        console.error("[v0] Error updating user session:", error)
        return false
      }

      console.log("[v0] User session updated successfully")
      return true
    } catch (error) {
      console.error("[v0] Database error updating session:", error)
      return false
    }
  }

  async saveLoanApplication(applicationData: LoanApplicationData): Promise<string | null> {
    try {
      console.log("[v0] Saving loan application to database:", applicationData)

      const { data, error } = await this.supabase
        .from("loan_applications")
        .insert(applicationData)
        .select("id")
        .single()

      if (error) {
        console.error("[v0] Supabase error saving loan application:", error)
        console.error("[v0] Error details:", error.message, error.details, error.hint)
        return null
      }

      console.log("[v0] Loan application saved successfully with data:", data)
      return data.id
    } catch (error) {
      console.error("[v0] Database error saving application:", error)
      return null
    }
  }

  async saveCustomerFeedback(feedbackData: CustomerFeedbackData): Promise<boolean> {
    try {
      console.log("[v0] Saving customer feedback to database:", feedbackData)

      const { data, error } = await this.supabase.from("customer_feedback").insert(feedbackData).select()

      if (error) {
        console.error("[v0] Supabase error saving customer feedback:", error)
        console.error("[v0] Error details:", error.message, error.details, error.hint)
        return false
      }

      console.log("[v0] Customer feedback saved successfully with data:", data)
      return true
    } catch (error) {
      console.error("[v0] Database error saving feedback:", error)
      return false
    }
  }

  async saveModelEvaluation(evaluationData: ModelEvaluationData): Promise<boolean> {
    try {
      console.log("[v0] Saving model evaluation:", evaluationData) // Added logging

      const { error } = await this.supabase.from("model_evaluation_metrics").insert(evaluationData)

      if (error) {
        console.error("[v0] Error saving model evaluation:", error)
        return false
      }

      console.log("[v0] Model evaluation saved successfully") // Added success logging
      return true
    } catch (error) {
      console.error("[v0] Database error saving evaluation:", error)
      return false
    }
  }
}

export const databaseService = new DatabaseService()
