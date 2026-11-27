import { useState, type FormEvent } from "react";
import axios from "axios";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  LoaderCircle,
  Play,
  Server,
  XCircle,
} from "lucide-react";

import { useMLHealth, useMLPrediction, useModelInfo } from "./hooks/useML";
import type {
  ModelMetrics,
  PredictionRequest,
} from "./services/mlService";

const fields = [
  {
    key: "RevolvingUtilizationOfUnsecuredLines",
    label: "Revolving utilization",
    description: "Unsecured credit utilization ratio",
    required: true,
  },
  {
    key: "NumberOfTime30-59DaysPastDueNotWorse",
    label: "Delinquencies: 30–59 days",
    description: "Number of past-due occurrences",
    required: true,
  },
  {
    key: "DebtRatio",
    label: "Debt ratio",
    description: "Dataset-specific debt ratio",
    required: true,
  },
  {
    key: "MonthlyIncome",
    label: "Monthly income",
    description: "May be omitted if unavailable",
    required: false,
  },
  {
    key: "NumberOfOpenCreditLinesAndLoans",
    label: "Open credit lines and loans",
    description: "Number of open accounts",
    required: true,
  },
  {
    key: "NumberOfTimes90DaysLate",
    label: "Delinquencies: 90+ days",
    description: "Number of past-due occurrences",
    required: true,
  },
  {
    key: "NumberRealEstateLoansOrLines",
    label: "Real estate loans or lines",
    description: "Number of real estate accounts",
    required: true,
  },
  {
    key: "NumberOfTime60-89DaysPastDueNotWorse",
    label: "Delinquencies: 60–89 days",
    description: "Number of past-due occurrences",
    required: true,
  },
] as const;

type FieldKey = (typeof fields)[number]["key"];

const initialValues: Record<FieldKey, string> = {
  RevolvingUtilizationOfUnsecuredLines: "",
  "NumberOfTime30-59DaysPastDueNotWorse": "",
  DebtRatio: "",
  MonthlyIncome: "",
  NumberOfOpenCreditLinesAndLoans: "",
  NumberOfTimes90DaysLate: "",
  NumberRealEstateLoansOrLines: "",
  "NumberOfTime60-89DaysPastDueNotWorse": "",
};

function formatMetric(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-muted/50 p-3">
      <p className="text-xs text-text-secondary">{label}</p>
      <p className="mt-1 text-lg font-semibold text-text-primary">
        {formatMetric(value)}
      </p>
    </div>
  );
}

function MetricsPanel({
  title,
  metrics,
}: {
  title: string;
  metrics: ModelMetrics;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h4 className="mb-4 font-medium text-text-primary">{title}</h4>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <Metric label="ROC-AUC" value={metrics.roc_auc} />
        <Metric label="PR-AUC" value={metrics.pr_auc} />
        <Metric label="Precision" value={metrics.precision} />
        <Metric label="Recall" value={metrics.recall} />
        <Metric label="F1 score" value={metrics.f1} />
      </div>
    </div>
  );
}

function getErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item: { msg?: string }) => item.msg ?? "Invalid input")
        .join("; ");
    }

    if (!error.response) {
      return "Cannot connect to the ML API.";
    }
  }

  return "Prediction request failed.";
}

export function CreditScoringPage() {
  const [values, setValues] = useState(initialValues);
  const [formError, setFormError] = useState<string | null>(null);
  const health = useMLHealth();
  const modelInfo = useModelInfo();
  const prediction = useMLPrediction();

  const modelAvailable = health.data?.model_available === true;

  function updateField(key: FieldKey, value: string) {
    setValues((current) => ({ ...current, [key]: value }));
    setFormError(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    for (const field of fields) {
      const rawValue = values[field.key].trim();

      if (!rawValue) {
        if (field.required) {
          setFormError(`${field.label} is required.`);
          return;
        }
        continue;
      }

      const numericValue = Number(rawValue);

      if (!Number.isFinite(numericValue) || numericValue < 0) {
        setFormError(`${field.label} must be a finite non-negative number.`);
        return;
      }
    }

    const payload: PredictionRequest = {
      RevolvingUtilizationOfUnsecuredLines: Number(
        values.RevolvingUtilizationOfUnsecuredLines,
      ),
      "NumberOfTime30-59DaysPastDueNotWorse": Number(
        values["NumberOfTime30-59DaysPastDueNotWorse"],
      ),
      DebtRatio: Number(values.DebtRatio),
      NumberOfOpenCreditLinesAndLoans: Number(
        values.NumberOfOpenCreditLinesAndLoans,
      ),
      NumberOfTimes90DaysLate: Number(values.NumberOfTimes90DaysLate),
      NumberRealEstateLoansOrLines: Number(
        values.NumberRealEstateLoansOrLines,
      ),
      "NumberOfTime60-89DaysPastDueNotWorse": Number(
        values["NumberOfTime60-89DaysPastDueNotWorse"],
      ),
    };

    if (values.MonthlyIncome.trim() !== "") {
      payload.MonthlyIncome = Number(values.MonthlyIncome);
    }

    prediction.mutate(payload);
  }

  function resetForm() {
    setValues(initialValues);
    setFormError(null);
    prediction.reset();
  }

  const randomForest = modelInfo.data?.results.random_forest;
  const logisticRegression = modelInfo.data?.results.logistic_regression;

  return (
    <div className="space-y-8">
      <header>
        <div className="flex items-center gap-3">
          <div className="flex size-11 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <BrainCircuit size={22} />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-text-primary">
              Credit Risk Lab
            </h2>
            <p className="mt-1 text-sm text-text-secondary">
              Experimental machine learning inference
            </p>
          </div>
        </div>
      </header>

      <section className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 shrink-0 text-amber-500" size={19} />
          <div>
            <p className="text-sm font-semibold text-text-primary">
              Experimental model — not for lending decisions
            </p>
            <p className="mt-1 text-sm leading-relaxed text-text-secondary">
              This model was trained on the historical Give Me Some Credit
              dataset. Its output is an uncalibrated historical event score,
              not a probability of default for an actual applicant. Do not
              use real customer data or use this result to approve or reject
              credit applications.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <Server size={17} />
            <span className="text-sm">API status</span>
          </div>
          <div className="mt-3 flex items-center gap-2">
            {health.isLoading ? (
              <LoaderCircle className="animate-spin text-text-secondary" size={17} />
            ) : health.data?.status === "available" ? (
              <CheckCircle2 className="text-success" size={18} />
            ) : (
              <XCircle className="text-danger" size={18} />
            )}
            <span className="font-semibold text-text-primary">
              {health.isLoading
                ? "Checking API..."
                : health.isError
                  ? "API connection failed"
                  : health.data?.model_available
                    ? "Model artifact available"
                    : "Model artifact unavailable"}
            </span>
          </div>
          {health.data?.model_name && (
            <p className="mt-2 text-xs text-text-secondary">
              {health.data.model_name} · v{health.data.model_version}
            </p>
          )}
          {health.isError && (
            <p className="mt-2 text-xs text-danger">
              Could not reach the ML API.
            </p>
          )}
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <Activity size={17} />
            <span className="text-sm">Model configuration</span>
          </div>
          {modelInfo.data ? (
            <>
              <p className="mt-3 font-semibold text-text-primary">
                {modelInfo.data.model_name}
              </p>
              <p className="mt-1 text-xs text-text-secondary">
                Version {modelInfo.data.model_version} ·{" "}
                {modelInfo.data.dataset_rows.toLocaleString("en-US")} records
              </p>
              <p className="mt-2 text-xs text-text-secondary">
                Threshold: {modelInfo.data.selected_threshold} · Target:{" "}
                {modelInfo.data.target}
              </p>
            </>
          ) : (
            <p className="mt-3 text-sm text-text-secondary">
              {modelInfo.isLoading
                ? "Loading model metadata..."
                : "Model metadata unavailable."}
            </p>
          )}
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-6">
        <div className="mb-5">
          <h3 className="font-semibold text-text-primary">
            Manual prediction
          </h3>
          <p className="mt-1 text-sm text-text-secondary">
            Enter the eight features expected by the training pipeline.
            Monthly income is optional.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-5 sm:grid-cols-2">
            {fields.map((field) => (
              <label key={field.key} className="block">
                <span className="text-sm font-medium text-text-primary">
                  {field.label}
                  {field.required && (
                    <span className="ml-1 text-danger">*</span>
                  )}
                </span>
                <span className="mt-1 block text-xs text-text-secondary">
                  {field.description}
                </span>
                <input
                  type="number"
                  min="0"
                  step="any"
                  required={field.required}
                  value={values[field.key]}
                  onChange={(event) =>
                    updateField(field.key, event.target.value)
                  }
                  placeholder={field.required ? "Enter value" : "Optional"}
                  className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-text-primary outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </label>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={!modelAvailable || prediction.isPending}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {prediction.isPending ? (
                <LoaderCircle className="animate-spin" size={16} />
              ) : (
                <Play size={16} />
              )}
              Run prediction
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="rounded-lg border border-border px-4 py-2.5 text-sm font-medium text-text-secondary transition hover:bg-surface-hover"
            >
              Reset
            </button>
          </div>

          {formError && (
            <p role="alert" className="mt-3 text-sm text-danger">
              {formError}
            </p>
          )}

          {!modelAvailable && !health.isLoading && (
            <p className="mt-3 text-xs text-text-secondary">
              {health.isError
                ? "Prediction is disabled because the ML API could not be reached."
                : "Prediction is disabled because the model artifact is unavailable on the API server."}
            </p>
          )}
        </form>
      </section>

      {prediction.isError && (
        <section className="rounded-xl border border-danger/30 bg-danger/5 p-4">
          <p className="text-sm font-medium text-danger">
            {getErrorMessage(prediction.error)}
          </p>
        </section>
      )}

      {prediction.data && (
        <section className="rounded-xl border border-border bg-card p-6">
          <div className="mb-5 flex items-center gap-2">
            <Activity className="text-primary" size={19} />
            <h3 className="font-semibold text-text-primary">
              Prediction result
            </h3>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-xs text-text-secondary">
                Uncalibrated model score (0–1)
              </p>
              <p className="mt-2 text-2xl font-semibold text-text-primary">
                {prediction.data.historical_event_score.toFixed(4)}
              </p>
            </div>
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-xs text-text-secondary">Raw score threshold</p>
              <p className="mt-2 text-2xl font-semibold text-text-primary">
                {prediction.data.threshold.toFixed(4)}
              </p>
            </div>
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-xs text-text-secondary">Model output</p>
              <p className="mt-2 text-2xl font-semibold text-text-primary">
                {prediction.data.prediction}
              </p>
            </div>
          </div>

          <div className="mt-4 rounded-lg border border-border p-4">
            <p className="text-sm font-medium text-text-primary">
              {prediction.data.prediction === 1
                ? "Serious delinquency in source dataset: yes"
                : "Serious delinquency in source dataset: no"}
            </p>
            <p className="mt-1 text-xs text-text-secondary">
              Target: {prediction.data.target}. Class 1 means serious
              delinquency within two years in the source dataset; class 0 means
              no such event. This is not a lending recommendation.
            </p>
            <p className="mt-2 text-xs text-text-secondary">
              Calibration: {prediction.data.probability_calibrated
                ? "Calibrated"
                : "Not calibrated"}
              {" · "}
              Model: {prediction.data.model_name} v
              {prediction.data.model_version}
            </p>
          </div>
        </section>
      )}

      {modelInfo.isError && (
        <p className="text-sm text-text-secondary">
          Model evaluation metrics could not be loaded.
        </p>
      )}

      {randomForest && logisticRegression && (
        <section className="space-y-4">
          <div>
            <h3 className="font-semibold text-text-primary">
              Model evaluation
            </h3>
            <p className="mt-1 text-sm text-text-secondary">
              Validation and test metrics from the offline experiment.
              These are dataset evaluation metrics, not live prediction quality.
            </p>
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-text-primary">
                Random Forest
              </h4>
              <MetricsPanel title="Test set" metrics={randomForest.test} />
              <MetricsPanel
                title="Validation set"
                metrics={randomForest.validation}
              />
            </div>
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-text-primary">
                Logistic Regression
              </h4>
              <MetricsPanel
                title="Test set"
                metrics={logisticRegression.test}
              />
              <MetricsPanel
                title="Validation set"
                metrics={logisticRegression.validation}
              />
            </div>
          </div>

          <p className="text-xs leading-relaxed text-text-secondary">
            The selected Random Forest model was chosen using validation
            PR-AUC. Test metrics were measured before the final model was
            refitted on the combined training and validation data.
          </p>
        </section>
      )}
    </div>
  );
}
