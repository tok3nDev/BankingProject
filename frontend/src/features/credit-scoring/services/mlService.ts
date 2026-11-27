import { api } from "@/lib/api";

export interface MLHealth {
  status: "available" | "unavailable";
  model_available: boolean;
  metadata_available: boolean;
  model_name: string | null;
  model_version: string | null;
}

export interface ModelMetrics {
  roc_auc: number;
  pr_auc: number;
  precision: number;
  recall: number;
  f1: number;
}

export interface ModelResult {
  selected_threshold: number;
  validation: ModelMetrics;
  test: ModelMetrics;
}

export interface ModelInfo {
  model_name: string;
  model_version: string;
  dataset: string;
  dataset_rows: number;
  features: string[];
  target: string;
  selected_threshold: number;
  probability_calibrated: false;
  results: Record<string, ModelResult>;
}

export interface PredictionRequest {
  RevolvingUtilizationOfUnsecuredLines: number;
  "NumberOfTime30-59DaysPastDueNotWorse": number;
  DebtRatio: number;
  MonthlyIncome?: number | null;
  NumberOfOpenCreditLinesAndLoans: number;
  NumberOfTimes90DaysLate: number;
  NumberRealEstateLoansOrLines: number;
  "NumberOfTime60-89DaysPastDueNotWorse": number;
}

export interface PredictionResponse {
  model_name: string;
  model_version: string;
  historical_event_score: number;
  threshold: number;
  prediction: 0 | 1;
  probability_calibrated: false;
  target: string;
}

export const mlService = {
  async getHealth(): Promise<MLHealth> {
    const response = await api.get<MLHealth>("/ml/health");
    return response.data;
  },

  async getModelInfo(): Promise<ModelInfo> {
    const response = await api.get<ModelInfo>("/ml/model-info");
    return response.data;
  },

  async predict(data: PredictionRequest): Promise<PredictionResponse> {
    const response = await api.post<PredictionResponse>(
      "/ml/predict",
      data,
    );
    return response.data;
  },
};
