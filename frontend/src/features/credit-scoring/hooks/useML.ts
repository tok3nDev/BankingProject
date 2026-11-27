import { useMutation, useQuery } from "@tanstack/react-query";

import {
  mlService,
  type PredictionRequest,
} from "../services/mlService";

export const mlKeys = {
  all: ["ml"] as const,
  health: () => [...mlKeys.all, "health"] as const,
  modelInfo: () => [...mlKeys.all, "model-info"] as const,
};

export function useMLHealth() {
  return useQuery({
    queryKey: mlKeys.health(),
    queryFn: mlService.getHealth,
    refetchInterval: 30_000,
  });
}

export function useModelInfo() {
  return useQuery({
    queryKey: mlKeys.modelInfo(),
    queryFn: mlService.getModelInfo,
  });
}

export function useMLPrediction() {
  return useMutation({
    mutationFn: (data: PredictionRequest) => mlService.predict(data),
  });
}
