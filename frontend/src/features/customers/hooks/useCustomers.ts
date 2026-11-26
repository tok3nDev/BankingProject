
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { dashboardKeys } from "@/features/dashboard/hooks/useDashboard";
import type {
  CustomerCreate,
  CustomerUpdate,
  PaginatedParams,
} from "@/types/api";
import { customerService } from "../services/customerService";

export const customerKeys = {
  all: ["customers"] as const,
  lists: () => [...customerKeys.all, "list"] as const,
  list: (params?: PaginatedParams) =>
    [...customerKeys.lists(), params] as const,
  details: () => [...customerKeys.all, "detail"] as const,
  detail: (id: string) => [...customerKeys.details(), id] as const,
};

export function useCustomers(params?: PaginatedParams) {
  return useQuery({
    queryKey: customerKeys.list(params),
    queryFn: () => customerService.getAll(params),
  });
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: customerKeys.detail(id),
    queryFn: () => customerService.getById(id),
    enabled: Boolean(id),
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CustomerCreate) => customerService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: customerKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: dashboardKeys.all,
      });
    },
  });
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: CustomerUpdate;
    }) => customerService.update(id, data),
    onSuccess: (customer) => {
      queryClient.setQueryData(
        customerKeys.detail(customer.id),
        customer,
      );

      queryClient.invalidateQueries({
        queryKey: customerKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: dashboardKeys.all,
      });
    },
  });
}
