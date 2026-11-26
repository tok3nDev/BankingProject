
import { api } from "@/lib/api";
import type {
  ApplicationCreate,
  CreditApplication,
  PaginatedParams,
} from "@/types/api";

export const applicationService = {
  async getAll(params?: PaginatedParams): Promise<CreditApplication[]> {
    const response = await api.get<CreditApplication[]>("/applications", {
      params,
    });
    return response.data;
  },

  async getById(id: string): Promise<CreditApplication> {
    const response = await api.get<CreditApplication>(`/applications/${id}`);
    return response.data;
  },

  async getByCustomer(
    customerId: string,
    params?: PaginatedParams,
  ): Promise<CreditApplication[]> {
    const response = await api.get<CreditApplication[]>(
      `/applications/customer/${customerId}`,
      { params },
    );
    return response.data;
  },

  async create(data: ApplicationCreate): Promise<CreditApplication> {
    const response = await api.post<CreditApplication>(
      "/applications",
      data,
    );
    return response.data;
  },
};
