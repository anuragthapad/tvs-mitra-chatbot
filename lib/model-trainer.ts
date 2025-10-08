export interface TrainingData {
  features: Record<string, any>[]
  labels: number[]
}

export interface ModelWeights {
  featureImportances: Record<string, number>
  classWeights: { approved: number; declined: number }
  thresholds: Record<string, number>
}

export class LoanApprovalModel {
  private weights: ModelWeights
  private isTrained = false
  private calculatedMetrics: Record<string, number> = {}

  constructor() {
    this.weights = {
      featureImportances: {
        // Primary factors (highest importance)
        LTV: 0.19, // Increased from 0.18 to redistribute gender weight
        Net_salary: 0.16, // Increased from 0.15 to redistribute gender weight
        Income_to_Loan_Ratio: 0.13, // Increased from 0.12 to redistribute gender weight
        Age: 0.11, // Increased from 0.1 to redistribute gender weight
        Employment_Type: 0.09, // Increased from 0.08 to redistribute gender weight

        // Secondary factors (medium importance)
        Loan_Amount: 0.07,
        State_Avg_Salary: 0.06,
        PAST_LOANS_ACTIVE: 0.05,
        Final_Tier: 0.04,
        Qualifications: 0.04,

        // Interaction factors (lower importance)
        Age_Group: 0.03,
        Income_Presence: 0.02,
        Salary_vs_State_Avg_Ratio: 0.02,
        PastLoans_Employment_Interaction: 0.01,
      },
      classWeights: {
        approved: 0.6, // Slightly favor approvals for business growth
        declined: 0.4,
      },
      thresholds: {
        age_min: 18,
        age_max: 60,
        ltv_excellent: 60,
        ltv_good: 70,
        ltv_fair: 80,
        ltv_poor: 90,
        income_high: 50000,
        income_medium: 30000,
        income_low: 15000,
      },
    }
  }

  train(): void {
    console.log("[v0] Starting model training simulation...")

    this.isTrained = true

    const testData = this.generateTestData(1000)

    // Simulate LGBM training process
    const trainingIterations = 140 // n_estimators from Python code
    const learningRate = 0.1 // learning_rate from Python code

    for (let i = 0; i < trainingIterations; i++) {
      // Simulate gradient boosting iterations
      if (i % 20 === 0) {
        console.log(`[v0] Training iteration ${i}/${trainingIterations}`)
      }
    }

    this.calculateMetrics(testData)

    console.log("[v0] Model training completed with LGBM simulation")
  }

  private generateTestData(size: number): { features: Record<string, any>[]; labels: number[] } {
    const features: Record<string, any>[] = []
    const labels: number[] = []

    for (let i = 0; i < size; i++) {
      const age = Math.floor(Math.random() * 42) + 18 // 18-60
      const salary = Math.floor(Math.random() * 80000) + 10000 // 10k-90k
      const loanAmount = Math.floor(Math.random() * 500000) + 50000 // 50k-550k
      const ltv = (loanAmount / (loanAmount * 1.2)) * 100 // Simulate LTV

      const employmentTypes = ["SAL", "AGR", "SEP", "STU", "NPP", "NREGI", "PEN", "NONEARNMEM", "NA"]
      const qualifications = ["HSC", "SSC", "UG", "GRAD", "PG", "OTHERS"]

      const feature = {
        Age: age,
        Net_salary: salary,
        Loan_Amount: loanAmount,
        LTV: ltv,
        Employment_Type: employmentTypes[Math.floor(Math.random() * employmentTypes.length)],
        Qualifications: qualifications[Math.floor(Math.random() * qualifications.length)],
        Income_to_Loan_Ratio: salary > 0 ? loanAmount / salary : 0,
        PAST_LOANS_ACTIVE: Math.random() > 0.3 ? "NO_PAST_LOANS" : "PAST_LOANS_ACTIVE",
        Final_Tier: Math.random() > 0.5 ? "Tier 1" : Math.random() > 0.5 ? "Tier 2" : "Tier 3",
      }

      features.push(feature)

      const probability = this.generateTrainingLabel(feature, ltv)
      labels.push(probability > 0.45 ? 1 : 0)
    }

    return { features, labels }
  }

  private generateTrainingLabel(feature: Record<string, any>, ltv: number): number {
    let score = 0.5

    // Simple scoring for training data generation
    if (ltv <= 60) score += 0.25
    else if (ltv <= 70) score += 0.15
    else if (ltv <= 80) score += 0.05
    else if (ltv <= 90) score -= 0.1
    else score -= 0.25

    const salary = feature.Net_salary || 0
    if (salary >= 50000) score += 0.2
    else if (salary >= 30000) score += 0.1
    else if (salary >= 15000) score += 0.05
    else if (salary === 0) score -= 0.3

    const age = feature.Age || 0
    if (age >= 25 && age <= 45) score += 0.15
    else if (age >= 18 && age <= 60) score += 0.05
    else score -= 0.2

    const empType = feature.Employment_Type || ""
    if (["SAL"].includes(empType)) score += 0.15
    else if (["AGR", "NREGI"].includes(empType)) score += 0.05
    else if (["STU", "PEN"].includes(empType)) score -= 0.1

    return Math.max(0, Math.min(1, score))
  }

  private calculateMetrics(testData: { features: Record<string, any>[]; labels: number[] }): void {
    const predictions: number[] = []
    const probabilities: number[] = []

    // Get predictions for test data
    for (let i = 0; i < testData.features.length; i++) {
      const feature = testData.features[i]
      const prob = this.predict(feature, feature.LTV)
      probabilities.push(prob.probability)
      predictions.push(prob.probability > 0.45 ? 1 : 0)
    }

    // Calculate confusion matrix
    let tp = 0,
      tn = 0,
      fp = 0,
      fn = 0
    for (let i = 0; i < testData.labels.length; i++) {
      const actual = testData.labels[i]
      const predicted = predictions[i]

      if (actual === 1 && predicted === 1) tp++
      else if (actual === 0 && predicted === 0) tn++
      else if (actual === 0 && predicted === 1) fp++
      else if (actual === 1 && predicted === 0) fn++
    }

    // Calculate metrics
    const accuracy = (tp + tn) / (tp + tn + fp + fn)
    const precision = tp / (tp + fp) || 0
    const recall = tp / (tp + fn) || 0
    const f1_score = (2 * (precision * recall)) / (precision + recall) || 0

    // Calculate AUC (simplified approximation)
    const sortedProbs = probabilities
      .map((prob, idx) => ({ prob, label: testData.labels[idx] }))
      .sort((a, b) => b.prob - a.prob)

    let auc = 0
    const positives = testData.labels.filter((l) => l === 1).length
    const negatives = testData.labels.length - positives

    if (positives > 0 && negatives > 0) {
      let tpr = 0,
        fpr = 0
      let prevFpr = 0

      for (const item of sortedProbs) {
        if (item.label === 1) tpr += 1 / positives
        else fpr += 1 / negatives

        auc += tpr * (fpr - prevFpr)
        prevFpr = fpr
      }
    }

    const gini_coefficient = 2 * auc - 1

    this.calculatedMetrics = {
      accuracy: Math.round(accuracy * 1000) / 1000,
      precision: Math.round(precision * 1000) / 1000,
      recall: Math.round(recall * 1000) / 1000,
      f1_score: Math.round(f1_score * 1000) / 1000,
      roc_auc: Math.round(auc * 1000) / 1000,
      gini_coefficient: Math.round(gini_coefficient * 1000) / 1000,
    }

    console.log("[v0] Calculated metrics:", this.calculatedMetrics)
  }

  predict(
    engineeredFeatures: Record<string, any>,
    ltv: number,
  ): { probability: number; approved: boolean; rocAuc: number } {
    if (!this.isTrained) {
      this.train()
    }

    console.log("[v0] Making prediction with features:", engineeredFeatures)

    let score = 0.5 // Base probability

    // LTV - Most important feature (19% importance)
    const ltvWeight = this.weights.featureImportances.LTV
    if (ltv <= this.weights.thresholds.ltv_excellent) score += 0.25 * ltvWeight
    else if (ltv <= this.weights.thresholds.ltv_good) score += 0.15 * ltvWeight
    else if (ltv <= this.weights.thresholds.ltv_fair) score += 0.05 * ltvWeight
    else if (ltv <= this.weights.thresholds.ltv_poor) score -= 0.1 * ltvWeight
    else score -= 0.25 * ltvWeight

    // Net_salary - Second most important (16% importance)
    const salaryWeight = this.weights.featureImportances.Net_salary
    const salary = engineeredFeatures.Net_salary || 0
    if (salary >= this.weights.thresholds.income_high) score += 0.25 * salaryWeight
    else if (salary >= this.weights.thresholds.income_medium) score += 0.15 * salaryWeight
    else if (salary >= this.weights.thresholds.income_low) score += 0.05 * salaryWeight
    else if (salary === 0 && engineeredFeatures.Income_Presence === "No Income") score -= 0.3 * salaryWeight

    // Income_to_Loan_Ratio - Third most important (13% importance)
    const ratioWeight = this.weights.featureImportances.Income_to_Loan_Ratio
    const incomeRatio = engineeredFeatures.Income_to_Loan_Ratio || 0
    if (incomeRatio > 0 && incomeRatio < 3) score += 0.15 * ratioWeight
    else if (incomeRatio >= 3 && incomeRatio < 6) score += 0.05 * ratioWeight
    else if (incomeRatio >= 10) score -= 0.2 * ratioWeight

    // Age - Fourth most important (11% importance)
    const ageWeight = this.weights.featureImportances.Age
    const age = engineeredFeatures.Age || 0
    if (age >= 25 && age <= 45) score += 0.15 * ageWeight
    else if (age >= 18 && age <= 60) score += 0.05 * ageWeight
    else score -= 0.2 * ageWeight

    // Employment_Type - Fifth most important (9% importance)
    const empWeight = this.weights.featureImportances.Employment_Type
    const empType = engineeredFeatures.Employment_Type || ""
    if (["SAL", "GOVT"].includes(empType)) score += 0.2 * empWeight
    else if (["BUS", "NREGI"].includes(empType)) score += 0.1 * empWeight
    else if (["STU", "PEN"].includes(empType)) score -= 0.1 * empWeight
    else if (["NON_APP", "Nonearnmem"].includes(empType)) score -= 0.15 * empWeight

    // Apply remaining feature weights
    const qualWeight = this.weights.featureImportances.Qualifications
    const qual = engineeredFeatures.Qualifications || ""
    if (["GRAD", "POSTGRAD", "PHD"].includes(qual)) score += 0.1 * qualWeight
    else if (["UG", "DIPLOMA", "DIP"].includes(qual)) score += 0.05 * qualWeight

    const pastLoansWeight = this.weights.featureImportances.PAST_LOANS_ACTIVE
    if (engineeredFeatures.PAST_LOANS_ACTIVE === "NO_PAST_LOANS") score += 0.1 * pastLoansWeight
    else score -= 0.05 * pastLoansWeight

    const tierWeight = this.weights.featureImportances.Final_Tier
    const tier = engineeredFeatures.Final_Tier || ""
    if (tier === "Tier 1") score += 0.05 * tierWeight
    else if (tier === "Tier 3") score -= 0.05 * tierWeight

    // Apply class weights
    score = score * this.weights.classWeights.approved + (1 - score) * this.weights.classWeights.declined

    const probability = Math.max(0, Math.min(1, score))
    console.log("[v0] Final prediction probability:", probability)

    const rocAuc = this.calculatedMetrics.roc_auc || 0.0
    const approved = rocAuc >= 0.93

    console.log("[v0] ROC-AUC score:", rocAuc)
    console.log("[v0] Approval decision based on ROC-AUC >= 0.93:", approved)

    return { probability, approved, rocAuc }
  }

  getFeatureImportance(): Record<string, number> {
    return this.weights.featureImportances
  }

  getModelMetrics(): Record<string, number> {
    if (Object.keys(this.calculatedMetrics).length === 0) {
      // Fallback to default metrics if not trained yet
      return {
        accuracy: 0.0,
        precision: 0.0,
        recall: 0.0,
        f1_score: 0.0,
        roc_auc: 0.0,
        gini_coefficient: 0.0,
      }
    }
    return this.calculatedMetrics
  }
}

export const trainedModel = new LoanApprovalModel()
