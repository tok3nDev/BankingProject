
import { api } from "@/lib/api";
import type {
  CreditAssessment,
  PaginatedParams,
} from "@/types/api";

export interface AssessmentCreate {
  application_id: string;
  probability_of_default: number;
  credit_score: number;
  model_name: string;
  model_version: string;
  features: Record<string, unknown>;
}

export const assessmentService = {
  async getById(id: string): Promise<CreditAssessment> {
    const response = await api.get<CreditAssessment>(
      `/assessments/${id}`,
    );
    return response.data;
  },

  async getByApplication(
    applicationId: string,
    params?: PaginatedParams,
  ): Promise<CreditAssessment[]> {
    const response = await api.get<CreditAssessment[]>(
      `/assessments/application/${applicationId}`,
      { params },
    );
    return response.data;
  },

  async create(data: AssessmentCreate): Promise<CreditAssessment> {
    const { application_id, ...query } = data;

    const response = await api.post<CreditAssessment>(
      "/assessments",
      query,
      { params: { application_id } },
    );

    return response.data;
  },
};
