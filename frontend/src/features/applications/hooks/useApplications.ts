
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type {
  ApplicationCreate,
  PaginatedParams,
} from "@/types/api";
import { applicationService } from "../services/applicationService";

export const applicationKeys = {
  all: ["applications"] as const,
  details: () => [...applicationKeys.all, "detail"] as const,
  detail: (id: string) => [...applicationKeys.details(), id] as const,
  customer: (customerId: string, params?: PaginatedParams) =>
    [...applicationKeys.all, "customer", customerId, params] as const,
};

export function useApplication(id: string) {
  return useQuery({
    queryKey: applicationKeys.detail(id),
    queryFn: () => applicationService.getById(id),
    enabled: Boolean(id),
  });
}

export function useCustomerApplications(
  customerId: string,
  params?: PaginatedParams,
) {
  return useQuery({
    queryKey: applicationKeys.customer(customerId, params),
    queryFn: () => applicationService.getByCustomer(customerId, params),
    enabled: Boolean(customerId),
  });
}

export function useCreateApplication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ApplicationCreate) =>
      applicationService.create(data),
    onSuccess: (application) => {
      queryClient.invalidateQueries({
        queryKey: applicationKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: ["customers", "detail", application.customer_id],
      });
    },
  });
}
