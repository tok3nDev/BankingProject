
import { api } from "@/lib/api";
import type {
  Customer,
  CustomerCreate,
  CustomerUpdate,
  PaginatedParams,
} from "@/types/api";

export const customerService = {
  async getAll(params?: PaginatedParams): Promise<Customer[]> {
    const response = await api.get<Customer[]>("/customers", { params });
    return response.data;
  },

  async getById(id: string): Promise<Customer> {
    const response = await api.get<Customer>(`/customers/${id}`);
    return response.data;
  },

  async create(data: CustomerCreate): Promise<Customer> {
    const response = await api.post<Customer>("/customers", data);
    return response.data;
  },

  async update(id: string, data: CustomerUpdate): Promise<Customer> {
    const response = await api.patch<Customer>(`/customers/${id}`, data);
    return response.data;
  },
};
