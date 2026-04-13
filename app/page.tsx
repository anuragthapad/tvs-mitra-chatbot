"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  CheckCircle,
  Bot,
  User,
  Brain,
  Zap,
  Shield,
  Clock,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
} from "lucide-react"
import { PINCODE_MAP, MAKE_CODE_MAP } from "@/lib/data-maps"
import { performFeatureEngineering, type ApplicantData } from "@/lib/feature-engineering"
import { trainedModel } from "@/lib/model-trainer"
import { databaseService } from "@/lib/database"

interface Question {
  name: keyof ApplicantData
  prompt: string
  type: "number" | "select" | "text"
  options?: string[]
  min?: number
  max?: number
}

interface StoredData {
  userInputs: ApplicantData
  engineeredFeatures: any
  evaluationMetrics: any
  customerFeedback: {
    rating: number
    improvementAreas: string[]
  }
  timestamp: string
}

const temporaryStorage: StoredData[] = []

const questions: Question[] = [
  { name: "Age", prompt: "What is your age?", type: "number", min: 18, max: 60 },
  { name: "Pincode", prompt: "What is your 6-digit pincode?", type: "number", min: 100000, max: 999999 },
  {
    name: "Qualifications",
    prompt: "What is your highest qualification?",
    type: "select",
    options: ["HSC", "SSC", "UG", "GRAD", "PG", "OTHERS"],
  },
  {
    name: "Employment_Type",
    prompt: "What is your employment type?",
    type: "select",
    options: ["AGR", "SAL", "SEP", "STU", "NPP", "NREGI", "PEN", "NONEARNMEM", "NA"],
  },
  {
    name: "Net_salary",
    prompt: "What is your net annual salary? (Enter 0 if not applicable)",
    type: "number",
    min: 0,
  },
  {
    name: "Make_Code",
    prompt: "What is the make code of the vehicle?",
    type: "select",
    options: [
      "Apache",
      "City Plus",
      "Jupiter",
      "Mopeds",
      "Ntorq",
      "Radeon",
      "Raider",
      "Ronin",
      "Scooty",
      "Sport",
      "Tvs",
      "Zest",
    ],
  },
  { name: "Loan_Amount", prompt: "What is the loan amount you are applying for?", type: "number", min: 10000 },
  {
    name: "PAST_LOANS_ACTIVE",
    prompt: "Do you have any past active loans?",
    type: "select",
    options: ["PAST_LOANS_ACTIVE", "NO_PAST_LOANS"],
  },
]

export default function LoanChatbot() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Partial<ApplicantData>>({})
  const [currentAnswer, setCurrentAnswer] = useState("")
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [showQuestion, setShowQuestion] = useState(true)
  const [showFeedback, setShowFeedback] = useState(false)
  const [feedbackRating, setFeedbackRating] = useState(0)
  const [improvementAreas, setImprovementAreas] = useState<string[]>([])
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [allVariants, setAllVariants] = useState<string[]>([])
  const [engineeredFeatures, setEngineeredFeatures] = useState<any>(null)
  const [evaluationMetrics, setEvaluationMetrics] = useState<any>(null)
  const [showAllVariants, setShowAllVariants] = useState(false)
  const [sessionId, setSessionId] = useState<string>("")
  const [sessionStartTime, setSessionStartTime] = useState<Date>(new Date())
  const [questionStartTime, setQuestionStartTime] = useState<Date>(new Date())
  const [totalTimeSpent, setTotalTimeSpent] = useState<number>(0)
  const [loanApplicationId, setLoanApplicationId] = useState<string>("")

  useEffect(() => {
    const initializeSession = async () => {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      setSessionId(newSessionId)
      setSessionStartTime(new Date())
      setQuestionStartTime(new Date())

      await databaseService.createUserSession({
        session_id: newSessionId,
        total_time_spent: 0,
        questions_answered: 0,
        is_completed: false,
        user_agent: navigator.userAgent,
      })

      console.log("[v0] Session initialized:", newSessionId)
    }

    initializeSession()
  }, [])

  useEffect(() => {
    setQuestionStartTime(new Date())
  }, [currentQuestion])

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date()
      const timeSpent = Math.floor((now.getTime() - sessionStartTime.getTime()) / 1000)
      setTotalTimeSpent(timeSpent)

      if (sessionId && timeSpent % 30 === 0) {
        databaseService.updateUserSession(sessionId, {
          total_time_spent: timeSpent,
          questions_answered: currentQuestion + (Object.keys(answers).length > 0 ? 1 : 0),
        })
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [sessionStartTime, sessionId, currentQuestion, answers])

  const goToPreviousQuestion = () => {
    if (currentQuestion > 0) {
      setShowQuestion(false)
      setTimeout(() => {
        setCurrentQuestion(currentQuestion - 1)
        const prevQuestion = questions[currentQuestion - 1]
        setCurrentAnswer(String(answers[prevQuestion.name] || ""))
        setError("")
        setShowQuestion(true)
      }, 150)
    }
  }

  const goToNextQuestion = () => {
    if (currentQuestion < questions.length - 1 && answers[questions[currentQuestion].name] !== undefined) {
      setShowQuestion(false)
      setTimeout(() => {
        setCurrentQuestion(currentQuestion + 1)
        const nextQuestion = questions[currentQuestion + 1]
        setCurrentAnswer(String(answers[nextQuestion.name] || ""))
        setError("")
        setShowQuestion(true)
      }, 150)
    }
  }

  const handleSubmit = async () => {
    const question = questions[currentQuestion]
    let value: any = currentAnswer

    if (!currentAnswer.trim()) {
      setError("Please provide an answer")
      return
    }

    if (question.type === "number") {
      value = Number.parseFloat(currentAnswer)
      if (isNaN(value)) {
        setError("Please enter a valid number")
        return
      }
      if (question.min !== undefined && value < question.min) {
        setError(`Value must be at least ${question.min}`)
        return
      }
      if (question.max !== undefined && value > question.max) {
        setError(`Value must be at most ${question.max}`)
        return
      }
    }

    if (question.name === "Pincode" && !PINCODE_MAP[value]) {
      setError("Pincode not found in our service area")
      return
    }

    if (question.name === "Make_Code" && !MAKE_CODE_MAP[value]) {
      setError("Make code not available")
      return
    }

    setError("")
    const newAnswers = { ...answers, [question.name]: value }
    setAnswers(newAnswers)
    setCurrentAnswer("")

    if (sessionId) {
      await databaseService.updateUserSession(sessionId, {
        questions_answered: currentQuestion + 1,
        total_time_spent: Math.floor((new Date().getTime() - sessionStartTime.getTime()) / 1000),
      })
    }

    if (currentQuestion < questions.length - 1) {
      setShowQuestion(false)
      setTimeout(() => {
        setCurrentQuestion(currentQuestion + 1)
        setShowQuestion(true)
      }, 150)
    } else {
      setIsProcessing(true)
      setTimeout(async () => {
        try {
          console.log("[v0] Starting loan processing with answers:", newAnswers)
          const processedAnswers = {
            ...newAnswers,
            Net_salary: newAnswers.Net_salary as number, // Keep as annual salary for feature engineering
          } as ApplicantData

          const features = performFeatureEngineering(processedAnswers)
          const prediction = trainedModel.predict(features)
          const metrics = trainedModel.getModelMetrics()

          setEngineeredFeatures(features)
          setEvaluationMetrics(metrics)

          console.log("[v0] Model prediction:", prediction)

          const selectedMakeCode = newAnswers.Make_Code as string
          const { all } = getAllModelVariants(selectedMakeCode, newAnswers)
          setAllVariants(all)

          const applicationEndTime = new Date()
          const applicationTimeSpent = Math.floor((applicationEndTime.getTime() - sessionStartTime.getTime()) / 1000)

          const loanData = {
            session_id: sessionId,
            age: newAnswers.Age as number,
            annual_salary: newAnswers.Net_salary as number, // User input is already annual
            monthly_salary: (newAnswers.Net_salary as number) / 12, // Calculate monthly from annual
            loan_amount: newAnswers.Loan_Amount as number,
            pincode: String(newAnswers.Pincode),
            qualification: newAnswers.Qualifications as string,
            employment_type: newAnswers.Employment_Type as string,
            make_code: newAnswers.Make_Code as string,
            past_loans: newAnswers.PAST_LOANS_ACTIVE as string,
            ltv_ratio: features.LTV || (newAnswers.Loan_Amount as number) / (features.Avg_Model_Price || 100000),
            state: features.State || "",
            state_avg_salary: features.State_Avg_Salary || 0,
            avg_model_price: features.Avg_Model_Price || 0,
            final_tier: features.Final_Tier || "",
            age_bin: features.Age_Group || "",
            salary_bin: features.Income_Tier || "",
            ltv_bin: features.Loan_Amount_Band || "",
            employment_age_interaction: `${newAnswers.Employment_Type}_${features.Age_Group || "Unknown"}`,
            qualification_employment_interaction: `${newAnswers.Qualifications}_${newAnswers.Employment_Type}`,
            salary_ltv_ratio: (newAnswers.Net_salary as number) / (newAnswers.Loan_Amount as number),
            age_salary_ratio: (newAnswers.Age as number) / ((newAnswers.Net_salary as number) / 1000),
            approval_probability: prediction.probability || 0,
            is_approved: prediction.approved, // Now based on ROC-AUC >= 0.93
            recommended_models: all,
          }

          console.log("[v0] Attempting to save loan application with data:", loanData)
          const applicationId = await databaseService.saveLoanApplication(loanData)
          if (applicationId) {
            setLoanApplicationId(applicationId)
            console.log("[v0] Loan application saved with ID:", applicationId)
          } else {
            console.error("[v0] Failed to save loan application - no ID returned")
          }

          const evaluationData = {
            session_id: sessionId,
            model_version: "v1.0",
            accuracy: metrics.accuracy,
            precision_score: metrics.precision,
            recall: metrics.recall,
            f1_score: metrics.f1_score,
            roc_auc: metrics.roc_auc,
            gini_coefficient: metrics.gini_coefficient,
            training_data_size: 10000,
            feature_count: Object.keys(features).length,
            model_parameters: { type: "LGBM", features: Object.keys(features) },
            feature_importance: features,
            training_date: new Date().toISOString(),
          }

          console.log("[v0] Attempting to save model evaluation with data:", evaluationData)
          const evaluationSaved = await databaseService.saveModelEvaluation(evaluationData)
          if (evaluationSaved) {
            console.log("[v0] Model evaluation saved successfully")
          } else {
            console.error("[v0] Failed to save model evaluation")
          }

          // Save model prediction for detailed tracking
          const predictionData = {
            session_id: sessionId,
            loan_application_id: applicationId || undefined,
            input_features: features,
            prediction_score: prediction.probability || 0,
            prediction_class: prediction.approved,
            confidence_level: metrics.roc_auc,
            model_version: "v1.0",
          }

          console.log("[v0] Attempting to save model prediction with data:", predictionData)
          const predictionId = await databaseService.saveModelPrediction(predictionData)
          if (predictionId) {
            console.log("[v0] Model prediction saved with ID:", predictionId)
          }

          await databaseService.updateUserSession(sessionId, {
            is_completed: true,
            total_time_spent: applicationTimeSpent,
            questions_answered: questions.length,
          })

          setIsComplete(true)
        } catch (err) {
          console.error("[v0] Processing error:", err)
          setError(err instanceof Error ? err.message : "Processing failed")
        } finally {
          setIsProcessing(false)
        }
      }, 2000)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSubmit()
    }
  }

  const handleFeedbackSubmit = async () => {
    console.log("[v0] Feedback submitted:", { rating: feedbackRating, improvements: improvementAreas })

    const feedbackData = {
      session_id: sessionId,
      overall_satisfaction_rating: feedbackRating,
      improvement_areas: improvementAreas,
    }

    console.log("[v0] Attempting to save customer feedback with data:", feedbackData)
    const success = await databaseService.saveCustomerFeedback(feedbackData)
    if (success) {
      console.log("[v0] Feedback saved to database successfully")
    } else {
      console.error("[v0] Failed to save customer feedback to database")
    }

    const storedData: StoredData = {
      userInputs: answers as ApplicantData,
      engineeredFeatures: engineeredFeatures,
      evaluationMetrics: evaluationMetrics,
      customerFeedback: {
        rating: feedbackRating,
        improvementAreas: improvementAreas,
      },
      timestamp: new Date().toISOString(),
    }

    temporaryStorage.push(storedData)
    console.log("[v0] Data stored in temporary storage:", storedData)
    console.log("[v0] Total stored sessions:", temporaryStorage.length)

    setFeedbackSubmitted(true)
  }

  const resetChat = () => {
    setCurrentQuestion(0)
    setAnswers({})
    setCurrentAnswer("")
    setIsComplete(false)
    setError("")
    setIsProcessing(false)
    setShowQuestion(true)
    setShowFeedback(false)
    setFeedbackRating(0)
    setImprovementAreas([])
    setFeedbackSubmitted(false)
    setAllVariants([])
    setEngineeredFeatures(null)
    setEvaluationMetrics(null)
    setSessionId("")
    setSessionStartTime(new Date())
    setQuestionStartTime(new Date())
    setTotalTimeSpent(0)
    setLoanApplicationId("")
  }

  const StarRating = ({ rating, onRatingChange }: { rating: number; onRatingChange: (rating: number) => void }) => {
    const labels = ["⭐ Poor", "⭐⭐ Okay", "⭐⭐⭐ Good", "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"]

    return (
      <div className="space-y-3">
        <div className="grid grid-cols-1 gap-2">
          {labels.map((label, index) => (
            <button
              key={index}
              onClick={() => onRatingChange(index + 1)}
              className={`p-3 rounded-lg border-2 transition-all text-left ${
                rating === index + 1
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-gray-200 hover:border-gray-300 text-gray-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    )
  }

  const ImprovementAreas = ({
    selected,
    onSelectionChange,
  }: { selected: string[]; onSelectionChange: (areas: string[]) => void }) => {
    const options = [
      "Clearer decision",
      "More choices",
      "Talk to agent",
      "Faster flow",
      "Personalized offers",
      "Location-specific deals",
    ]

    const toggleOption = (option: string) => {
      if (selected.includes(option)) {
        onSelectionChange(selected.filter((item) => item !== option))
      } else {
        onSelectionChange([...selected, option])
      }
    }

    return (
      <div className="space-y-3">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {options.map((option) => (
            <button
              key={option}
              onClick={() => toggleOption(option)}
              className={`p-3 rounded-lg border-2 transition-all text-sm ${
                selected.includes(option)
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-gray-200 hover:border-gray-300 text-gray-700"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    )
  }

  const getAllModelVariants = (makeCode: string, answersData: Partial<ApplicantData>) => {
    const makeCodeData = MAKE_CODE_MAP[makeCode]
    if (!makeCodeData || makeCodeData.length === 0) {
      return { all: [] }
    }

    const variantsWithConfidence = makeCodeData.map((model: any) => {
      const baseConfidence = Math.random() * 0.4 + 0.6
      const ltvRatio = (answersData.Loan_Amount as number) / model.Avg_Model_Price
      const ltvAdjustment = ltvRatio > 0.8 ? -0.1 : ltvRatio < 0.5 ? 0.1 : 0
      const employmentBonus = ["SAL", "GOVT"].includes(answersData.Employment_Type as string) ? 0.05 : 0
      const age = answersData.Age as number
      const ageBonus = age >= 25 && age <= 45 ? 0.05 : 0

      const finalConfidence = Math.min(0.95, Math.max(0.5, baseConfidence + ltvAdjustment + employmentBonus + ageBonus))

      return {
        name: model.Model_Description,
        confidence: finalConfidence,
      }
    })

    const sortedVariants = variantsWithConfidence.sort((a, b) => b.confidence - a.confidence)

    return {
      all: sortedVariants.map((variant) => variant.name),
    }
  }

  if (isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md mx-4 animate-fade-in">
          <CardContent className="p-8 text-center">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
              <Brain className="h-10 w-10 text-secondary animate-pulse-slow" />
              <Zap className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-foreground">Processing Your Application</h3>
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-2 justify-center">
                <Shield className="h-4 w-4 text-secondary" />
                <span>Secure data processing</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <TrendingUp className="h-4 w-4 text-secondary" />
                <span>Real-time feature engineering</span>
              </div>
              <div className="flex items-center gap-2 justify-center">
                <Brain className="h-4 w-4 text-secondary" />
                <span>AI model prediction</span>
              </div>
            </div>
            <div className="mt-6 bg-muted rounded-lg p-3">
              <p className="text-xs text-muted-foreground">Your data is encrypted and processed securely</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isComplete && !showFeedback) {
    const displayedVariants = showAllVariants ? allVariants : allVariants.slice(0, 5)
    const hasMoreVariants = allVariants.length > 5

    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-6xl animate-slide-in-up">
          <CardHeader className="bg-secondary text-white">
            <CardTitle className="flex items-center justify-center gap-3 text-2xl">
              <CheckCircle className="h-8 w-8" />
              Eligible model variants for loan
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {displayedVariants.map((variantName, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg border-2 border-secondary/20 bg-secondary/5 transition-smooth hover:shadow-lg hover:border-secondary/40"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="bg-primary text-primary-foreground rounded-full w-7 h-7 flex items-center justify-center font-bold text-sm">
                          {index + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-base text-foreground truncate">{variantName}</h4>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {hasMoreVariants && (
                <div className="text-center">
                  <Button
                    onClick={() => setShowAllVariants(!showAllVariants)}
                    variant="outline"
                    className="px-6 py-2 text-sm transition-smooth"
                  >
                    {showAllVariants ? "View Less" : `View More (${allVariants.length - 5} more)`}
                  </Button>
                </div>
              )}
            </div>

            <div className="text-center mt-8 space-y-4">
              <Button
                onClick={() => window.open("https://www.tvscredit.com/loans/two-wheeler-loans/apply-now/", "_blank")}
                className="bg-secondary hover:bg-secondary/90 text-secondary-foreground px-8 py-3 text-lg transition-smooth mr-4 flex items-center justify-center gap-2"
              >
                Apply Now
                <ExternalLink className="h-4 w-4" />
              </Button>
              <Button
                onClick={() => setShowFeedback(true)}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-3 text-lg transition-smooth mr-4"
              >
                Provide Feedback
              </Button>
              <Button
                onClick={resetChat}
                className="bg-muted hover:bg-muted/90 text-muted-foreground px-8 py-3 text-lg transition-smooth"
              >
                Start New Application
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (showFeedback && !feedbackSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-2xl animate-slide-in-up">
          <CardHeader className="bg-primary text-primary-foreground">
            <CardTitle className="flex items-center justify-center gap-3 text-xl">
              <Bot className="h-6 w-6" />
              TVS Mitra - Customer Feedback
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">How nice was my reply?</h3>
                <StarRating rating={feedbackRating} onRatingChange={setFeedbackRating} />
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">
                  Tell us what can I be improved upon? (select one or more)
                </h3>
                <ImprovementAreas selected={improvementAreas} onSelectionChange={setImprovementAreas} />
              </div>

              <div className="flex gap-4 mt-8">
                <Button
                  onClick={handleFeedbackSubmit}
                  className="flex-1 bg-secondary hover:bg-secondary/90 text-secondary-foreground py-3 text-lg transition-smooth"
                  disabled={!feedbackRating}
                >
                  Submit Feedback
                </Button>
                <Button
                  onClick={() => setShowFeedback(false)}
                  variant="outline"
                  className="px-6 py-3 text-lg transition-smooth"
                >
                  Skip
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (feedbackSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-2xl animate-slide-in-up">
          <CardHeader className="bg-secondary text-secondary-foreground">
            <CardTitle className="flex items-center justify-center gap-3 text-xl">
              <Bot className="h-6 w-6" />
              TVS Mitra
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8 text-center">
            <div className="space-y-4">
              <CheckCircle className="h-16 w-16 text-secondary mx-auto" />
              <h3 className="text-2xl font-bold text-foreground">Thanks a ton for your feedback! 💙</h3>
              <p className="text-lg text-muted-foreground">
                Your inputs help me get better every day. Come back anytime, I'll be right here to assist you. ✨
              </p>
              <Button
                onClick={resetChat}
                className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-3 text-lg transition-smooth mt-6"
              >
                Start New Application
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const question = questions[currentQuestion]
  const progress = ((currentQuestion + 1) / questions.length) * 100
  const canGoBack = currentQuestion > 0
  const canGoForward = currentQuestion < questions.length - 1 && answers[questions[currentQuestion].name] !== undefined

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-2xl shadow-xl">
        <CardHeader className="bg-primary text-primary-foreground">
          <CardTitle className="flex items-center gap-3 text-xl">
            <Bot className="h-6 w-6" />
            TVS Mitra - Loan Application Assistant
            <div className="ml-auto flex items-center gap-2">
              <Shield className="h-5 w-5" />
              <Clock className="h-5 w-5" />
            </div>
          </CardTitle>
          <div className="space-y-2">
            <div className="w-full bg-primary-foreground/20 rounded-full h-3">
              <div
                className="h-3 bg-secondary rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm opacity-90">
              <span>
                Question {currentQuestion + 1} of {questions.length}
              </span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-8">
          <div className={`space-y-6 ${showQuestion ? "animate-slide-in-up" : "opacity-50"}`}>
            <div className="flex items-start gap-4">
              <div className="bg-primary/10 p-3 rounded-full">
                <Bot className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1">
                <div className="bg-card p-4 rounded-lg rounded-tl-none">
                  <p className="text-card-foreground font-medium">{question.prompt}</p>
                  {question.name === "Age" && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Age must be between 18-60 years for loan eligibility
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="bg-secondary/10 p-3 rounded-full">
                <User className="h-6 w-6 text-secondary" />
              </div>
              <div className="flex-1 space-y-3">
                {question.type === "select" ? (
                  <Select value={currentAnswer} onValueChange={setCurrentAnswer}>
                    <SelectTrigger className="focus-ring transition-smooth">
                      <SelectValue placeholder="Select an option" />
                    </SelectTrigger>
                    <SelectContent>
                      {question.options?.map((option) => (
                        <SelectItem key={option} value={option} className="transition-smooth">
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    type={question.type}
                    value={currentAnswer}
                    onChange={(e) => setCurrentAnswer(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter your answer"
                    min={question.min}
                    max={question.max}
                    className="focus-ring transition-smooth text-lg p-4"
                  />
                )}

                {error && (
                  <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 animate-fade-in">
                    <p className="text-destructive text-sm font-medium">{error}</p>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button
                    onClick={goToPreviousQuestion}
                    variant="outline"
                    className="flex items-center gap-2 px-4 py-3 transition-smooth focus-ring bg-transparent"
                    disabled={!canGoBack}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Back
                  </Button>

                  {canGoForward ? (
                    <Button
                      onClick={goToNextQuestion}
                      className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-3 text-lg font-medium transition-smooth focus-ring flex items-center justify-center gap-2"
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      onClick={handleSubmit}
                      className="flex-1 bg-secondary hover:bg-secondary/90 text-secondary-foreground py-3 text-lg font-medium transition-smooth focus-ring"
                      disabled={!currentAnswer.trim()}
                    >
                      {currentQuestion < questions.length - 1 ? "Continue" : "Submit Application"}
                    </Button>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-border">
              <div className="flex items-center justify-center gap-6 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Shield className="h-4 w-4" />
                  <span>Secure & Encrypted</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>Instant Processing</span>
                </div>
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  <span>AI-Powered</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
