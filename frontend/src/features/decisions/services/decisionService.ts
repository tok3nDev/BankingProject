
import { api } from "@/lib/api";
import type {
  CreditDecision,
  DecisionCreate,
  PaginatedParams,
} from "@/types/api";

export const decisionService = {
  async getById(id: string): Promise<CreditDecision> {
    const response = await api.get<CreditDecision>(
      `/decisions/${id}`,
    );
    return response.data;
  },

  async getByApplication(
    applicationId: string,
    params?: PaginatedParams,
  ): Promise<CreditDecision[]> {
    const response = await api.get<CreditDecision[]>(
      `/decisions/application/${applicationId}`,
      { params },
    );
    return response.data;
  },

  async create(data: DecisionCreate): Promise<CreditDecision> {
    const response = await api.post<CreditDecision>(
      "/decisions",
      data,
    );
    return response.data;
  },
};
