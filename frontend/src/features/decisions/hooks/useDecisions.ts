
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { DecisionCreate, PaginatedParams } from "@/types/api";
import { decisionService } from "../services/decisionService";

export const decisionKeys = {
  all: ["decisions"] as const,
  details: () => [...decisionKeys.all, "detail"] as const,
  detail: (id: string) => [...decisionKeys.details(), id] as const,
  application: (applicationId: string, params?: PaginatedParams) =>
    [...decisionKeys.all, "application", applicationId, params] as const,
};

export function useDecision(id: string) {
  return useQuery({
    queryKey: decisionKeys.detail(id),
    queryFn: () => decisionService.getById(id),
    enabled: Boolean(id),
  });
}

export function useApplicationDecisions(
  applicationId: string,
  params?: PaginatedParams,
) {
  return useQuery({
    queryKey: decisionKeys.application(applicationId, params),
    queryFn: () => decisionService.getByApplication(applicationId, params),
    enabled: Boolean(applicationId),
  });
}

export function useCreateDecision() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DecisionCreate) => decisionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: decisionKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: ["applications"],
      });
    },
  });
}
