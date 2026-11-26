
export type EmploymentStatus =
  | "employed"
  | "self_employed"
  | "unemployed"
  | "student"
  | "retired";

export interface Customer {
  id: string;
  full_name: string;
  date_of_birth: string | null;
  email: string | null;
  monthly_income: string | null;
  monthly_debt_payments: string | null;
  employment_months: number | null;
  employment_status: EmploymentStatus | null;
  created_at: string;
}

export interface CustomerCreate {
  full_name: string;
  date_of_birth?: string | null;
  email?: string | null;
  monthly_income: number;
  monthly_debt_payments: number;
  employment_months: number;
  employment_status: EmploymentStatus;
}

export interface CustomerUpdate {
  full_name?: string | null;
  date_of_birth?: string | null;
  email?: string | null;
  monthly_income?: number | null;
  monthly_debt_payments?: number | null;
  employment_months?: number | null;
  employment_status?: EmploymentStatus | null;
}

export type ApplicationStatus =
  | "pending"
  | "assessed"
  | "approved"
  | "rejected"
  | "withdrawn";

export interface CreditApplication {
  id: string;
  customer_id: string;
  requested_amount: string;
  currency_code: string;
  term_months: number;
  purpose: string;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  customer_id: string;
  requested_amount: number;
  currency_code: string;
  term_months: number;
  purpose: string;
}

export interface CreditAssessment {
  id: string;
  application_id: string;
  probability_of_default: string;
  credit_score: number;
  model_name: string;
  model_version: string;
  features: Record<string, unknown>;
  evaluated_at: string;
}

export type DecisionStatus =
  | "approved"
  | "rejected"
  | "manual_review";

export interface CreditDecision {
  id: string;
  application_id: string;
  assessment_id: string | null;
  decision_status: DecisionStatus;
  reason: string | null;
  decided_at: string;
}

export interface DecisionCreate {
  application_id: string;
  assessment_id?: string | null;
  decision_status: DecisionStatus;
  reason?: string | null;
}

export interface PaginatedParams {
  offset?: number;
  limit?: number;
}

export interface RequestedAmountByCurrency {
  currency_code: string;
  total_amount: string;
}

export interface RecentApplication {
  id: string;
  customer_name: string;
  requested_amount: string;
  currency_code: string;
  purpose: string;
  status: ApplicationStatus;
  created_at: string;
}

export interface DashboardStats {
  total_customers: number;
  total_applications: number;
  pending_applications: number;
  assessed_applications: number;
  approved_applications: number;
  rejected_applications: number;
  withdrawn_applications: number;
  requested_amount_by_currency: RequestedAmountByCurrency[];
  recent_applications: RecentApplication[];
}