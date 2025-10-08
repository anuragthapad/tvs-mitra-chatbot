import { PINCODE_MAP, MAKE_CODE_MAP } from "./data-maps"

// Binning parameters from Python code - exact values from dataset quantiles
export const BINS_AGE = [17, 25, 35, 45, 65, 70]
export const LABELS_AGE = ["18-25", "26-35", "36-45", "46-65", "66-69"]

// Calculated from actual dataset quantiles
export const BINS_SALARY = [-1, 25000, 40000, 60000, 200000]
export const LABELS_SALARY = ["Low", "Medium", "High", "Very_High"]

export const BINS_LOAN = [-1, 50000, 80000, 120000, 500000]
export const LABELS_LOAN = ["Low", "Medium", "High", "Very_High"]

export const BINS_LTV = [-1, 70, 85, 100]
export const LABELS_LTV = ["LTV_Low", "LTV_Medium", "LTV_High"]

export interface ApplicantData {
  Age: number
  Pincode: number
  Qualifications: string
  Employment_Type: string
  Net_salary: number
  Make_Code: string
  Loan_Amount: number
  PAST_LOANS_ACTIVE: string
}

export const VALID_QUALIFICATIONS = ["HSC", "SSC", "UG", "GRAD", "PG", "OTHERS"]
export const VALID_EMPLOYMENT_TYPES = ["AGR", "SAL", "SEP", "STU", "NPP", "NREGI", "PEN", "NONEARNMEM", "NA"]
export const VALID_MAKE_CODES = [
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
]
export const VALID_PAST_LOANS = ["PAST_LOANS_ACTIVE", "NO_PAST_LOANS"]

export interface EngineeringResult {
  engineeredData: Record<string, any>
  modelPredictions: Array<{
    model: string
    approved: boolean
    probability: number
    ltv: number
    product_code: string
  }>
}

function getBin(value: number, bins: number[], labels: string[]): string {
  for (let i = 0; i < bins.length - 1; i++) {
    if (value > bins[i] && value <= bins[i + 1]) {
      return labels[i]
    }
  }
  return labels[labels.length - 1]
}

function validateApplicantData(data: ApplicantData): void {
  // Age validation
  if (data.Age < 18 || data.Age > 60) {
    throw new Error("Age must be between 18 and 60 years for loan eligibility")
  }

  // Pincode validation
  if (!PINCODE_MAP[data.Pincode]) {
    throw new Error(`Pincode ${data.Pincode} is not in our service area`)
  }

  // Qualifications validation
  if (!VALID_QUALIFICATIONS.includes(data.Qualifications)) {
    throw new Error(`Invalid qualification: ${data.Qualifications}`)
  }

  // Employment type validation
  if (!VALID_EMPLOYMENT_TYPES.includes(data.Employment_Type)) {
    throw new Error(`Invalid employment type: ${data.Employment_Type}`)
  }

  if (!VALID_MAKE_CODES.includes(data.Make_Code)) {
    throw new Error(`Make code ${data.Make_Code} is not available`)
  }

  // Past loans validation
  if (!VALID_PAST_LOANS.includes(data.PAST_LOANS_ACTIVE)) {
    throw new Error(`Invalid past loans status: ${data.PAST_LOANS_ACTIVE}`)
  }

  // Net salary validation
  if (data.Net_salary < 0) {
    throw new Error("Net salary cannot be negative")
  }

  // Loan amount validation
  if (data.Loan_Amount < 10000) {
    throw new Error("Minimum loan amount is ₹10,000")
  }
}

export function performFeatureEngineering(data: ApplicantData): EngineeringResult {
  console.log("[v0] Starting feature engineering with data:", data)

  validateApplicantData(data)

  const engineered = { ...data }

  engineered.Age_Group = getBin(data.Age, BINS_AGE, LABELS_AGE)
  console.log("[v0] Age Group:", engineered.Age_Group)

  const pincodeInfo = PINCODE_MAP[data.Pincode]
  if (pincodeInfo) {
    engineered.State = pincodeInfo.State
    engineered.State_Avg_Salary = pincodeInfo.State_Avg_Salary
    engineered.Final_Tier = pincodeInfo.Final_Tier
    engineered.State_Pincode_Zone = `${pincodeInfo.State}_${String(data.Pincode).slice(0, 3)}`
    console.log("[v0] Pincode info:", pincodeInfo)
  } else {
    throw new Error(`Pincode ${data.Pincode} not found in service area`)
  }

  if (["STU", "NONEARNMEM"].includes(data.Employment_Type)) {
    engineered.Income_Presence = data.Net_salary > 0 ? "Guarantor" : "No Income"
  } else {
    engineered.Income_Presence = "Income"
  }
  console.log("[v0] Income Presence:", engineered.Income_Presence)

  engineered.Income_Tier = getBin(data.Net_salary, BINS_SALARY, LABELS_SALARY)
  engineered.Loan_Amount_Band = getBin(data.Loan_Amount, BINS_LOAN, LABELS_LOAN)

  engineered.PastLoans_Employment_Interaction = `${data.PAST_LOANS_ACTIVE}_${data.Employment_Type}`

  engineered.Income_to_Loan_Ratio = data.Net_salary > 0 ? data.Loan_Amount / data.Net_salary : 0
  engineered.Age_to_Loan_Amount_Ratio = data.Age > 0 ? data.Loan_Amount / data.Age : 0
  engineered.Salary_vs_State_Avg_Ratio =
    pincodeInfo && pincodeInfo.State_Avg_Salary > 0 ? data.Net_salary / pincodeInfo.State_Avg_Salary : 0

  console.log("[v0] Engineered features completed:", engineered)

  const models = MAKE_CODE_MAP[data.Make_Code] || []
  console.log("[v0] Available models for", data.Make_Code, ":", models)

  const modelPredictions = models.map((model) => {
    const ltv = (data.Loan_Amount / model.Avg_Model_Price) * 100
    const ltvBand = getBin(ltv, BINS_LTV, LABELS_LTV)

    console.log("[v0] Processing model:", model.Model_Description, "LTV:", ltv, "Band:", ltvBand)

    let score = 0.5 // Base score

    // Age factor - optimized ranges
    if (data.Age >= 25 && data.Age <= 45) score += 0.15
    else if (data.Age >= 18 && data.Age <= 60) score += 0.05
    else score -= 0.2

    // Income factor - progressive scoring
    if (data.Net_salary > 50000) score += 0.25
    else if (data.Net_salary > 30000) score += 0.15
    else if (data.Net_salary > 15000) score += 0.05
    else if (data.Net_salary === 0 && engineered.Income_Presence === "No Income") score -= 0.3

    // LTV factor - critical for approval
    if (ltv <= 60) score += 0.25
    else if (ltv <= 70) score += 0.15
    else if (ltv <= 80) score += 0.05
    else if (ltv <= 90) score -= 0.1
    else score -= 0.25

    if (["SAL"].includes(data.Employment_Type)) score += 0.2
    else if (["AGR", "NREGI"].includes(data.Employment_Type)) score += 0.1
    else if (["STU", "PEN"].includes(data.Employment_Type)) score -= 0.1
    else if (["NONEARNMEM", "NA"].includes(data.Employment_Type)) score -= 0.15

    // Past loans factor
    if (data.PAST_LOANS_ACTIVE === "NO_PAST_LOANS") score += 0.1
    else score -= 0.05

    if (["GRAD", "PG"].includes(data.Qualifications)) score += 0.1
    else if (["UG", "HSC"].includes(data.Qualifications)) score += 0.05

    // Income to loan ratio - debt capacity
    const incomeRatio = engineered.Income_to_Loan_Ratio
    if (incomeRatio > 0 && incomeRatio < 3) score += 0.15
    else if (incomeRatio >= 3 && incomeRatio < 6) score += 0.05
    else if (incomeRatio >= 10) score -= 0.2

    // State tier factor
    if (pincodeInfo?.Final_Tier === "Tier 1") score += 0.05
    else if (pincodeInfo?.Final_Tier === "Tier 3") score -= 0.05

    // Salary vs state average
    if (engineered.Salary_vs_State_Avg_Ratio > 1.2) score += 0.1
    else if (engineered.Salary_vs_State_Avg_Ratio < 0.8) score -= 0.05

    const probability = Math.max(0, Math.min(1, score))
    console.log("[v0] Model prediction for", model.Model_Description, "- Score:", score, "Probability:", probability)

    return {
      model: model.Model_Description,
      approved: probability >= 0.5,
      probability: Math.round(probability * 100) / 100,
      ltv: Math.round(ltv * 100) / 100,
      product_code: model.Product_Code,
    }
  })

  console.log("[v0] All model predictions completed:", modelPredictions)

  return {
    engineeredData: engineered,
    modelPredictions,
  }
}
