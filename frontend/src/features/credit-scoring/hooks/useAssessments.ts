
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import type { PaginatedParams } from "@/types/api";
import {
  assessmentService,
  type AssessmentCreate,
} from "../services/assessmentService";

export const assessmentKeys = {
  all: ["assessments"] as const,
  details: () => [...assessmentKeys.all, "detail"] as const,
  detail: (id: string) => [...assessmentKeys.details(), id] as const,
  application: (applicationId: string, params?: PaginatedParams) =>
    [...assessmentKeys.all, "application", applicationId, params] as const,
};

export function useAssessment(id: string) {
  return useQuery({
    queryKey: assessmentKeys.detail(id),
    queryFn: () => assessmentService.getById(id),
    enabled: Boolean(id),
  });
}

export function useApplicationAssessments(
  applicationId: string,
  params?: PaginatedParams,
) {
  return useQuery({
    queryKey: assessmentKeys.application(applicationId, params),
    queryFn: () =>
      assessmentService.getByApplication(applicationId, params),
    enabled: Boolean(applicationId),
  });
}

export function useCreateAssessment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AssessmentCreate) =>
      assessmentService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: ["applications"],
      });
    },
  });
}

export function useRunAssessment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (applicationId: string) =>
      assessmentService.run(applicationId),

  onSuccess: (_data, applicationId) => {
    queryClient.invalidateQueries({
      queryKey: [
        ...assessmentKeys.all,
        "application",
        applicationId,
      ],
    });

    queryClient.invalidateQueries({
      queryKey: ["applications"],
    });
  },
  });
}
