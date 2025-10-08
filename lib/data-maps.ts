import pincodeMapData from "./data/pincode-map.json"
import makeCodeMapData from "./data/make-code-map.json"

// Export the maps for use throughout the application
export const PINCODE_MAP = pincodeMapData
export const MAKE_CODE_MAP = makeCodeMapData

// Binning parameters extracted from Python code
export const BINS_AGE = [17, 25, 35, 45, 65, 70]
export const LABELS_AGE = ["18-25", "26-35", "36-45", "46-65", "66-69"]

export const BINS_LTV = [0, 33.33, 66.66, 100]
export const LABELS_LTV = ["LTV_Low", "LTV_Medium", "LTV_High"]

export const BINS_SALARY = [0, 25000, 40000, 60000, 100000]
export const LABELS_SALARY = ["Low", "Medium", "High", "Very_High"]

export const BINS_LOAN = [0, 50000, 100000, 150000, 300000]
export const LABELS_LOAN = ["Low", "Medium", "High", "Very_High"]

// Valid options for form validation
export const VALID_QUALIFICATIONS = ["SSC", "UG", "GRAD", "OTHERS", "POSTGRAD", "PHD", "DIP", "DIPLOMA", "N_A"]
export const VALID_EMPLOYMENT_TYPES = [
  "AGR",
  "SAL",
  "NREGI",
  "SEP",
  "STU",
  "PEN",
  "BUS",
  "OTHERS",
  "GOVT",
  "N_A",
  "Nonearnmem",
]
export const VALID_GENDERS = ["Male", "Female"]
export const VALID_PAST_LOANS = ["PAST_LOANS_ACTIVE", "NO_PAST_LOANS"]
