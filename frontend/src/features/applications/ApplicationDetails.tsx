
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  FileText,
  Play,
  LoaderCircle,
  CheckCircle2,
} from "lucide-react";

import { useApplication } from "./hooks/useApplications";
import { useCustomer } from "@/features/customers/hooks/useCustomers";
import {
  useApplicationAssessments,
  useRunAssessment,
} from "@/features/credit-scoring/hooks/useAssessments";
import {
  useApplicationDecisions,
  useCreateDecision,
} from "@/features/decisions/hooks/useDecisions";
import type {
  ApplicationStatus,
  DecisionStatus,
} from "@/types/api";

const statusStyles: Record<ApplicationStatus, string> = {
  pending: "bg-amber-500/10 text-amber-600",
  assessed: "bg-blue-500/10 text-blue-600",
  approved: "bg-green-500/10 text-green-600",
  rejected: "bg-red-500/10 text-red-600",
  withdrawn: "bg-muted text-muted-foreground",
};

const decisionStyles: Record<DecisionStatus, string> = {
  approved: "bg-green-500/10 text-green-600",
  rejected: "bg-red-500/10 text-red-600",
  manual_review: "bg-amber-500/10 text-amber-600",
};

function getFeatureNumber(
  features: Record<string, unknown>,
  key: string,
): number | null {
  const value = features[key];

  if (value === undefined || value === null) {
    return null;
  }

  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

export function ApplicationDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [decisionStatus, setDecisionStatus] =
    useState<DecisionStatus>("manual_review");
  const [decisionReason, setDecisionReason] = useState("");

  const applicationQuery = useApplication(id ?? "");
  const application = applicationQuery.data;

  const customerQuery = useCustomer(application?.customer_id ?? "");

  const assessmentsQuery = useApplicationAssessments(id ?? "", {
    offset: 0,
    limit: 100,
  });

  const decisionsQuery = useApplicationDecisions(id ?? "", {
    offset: 0,
    limit: 100,
  });

  const runAssessment = useRunAssessment();
  const createDecision = useCreateDecision();

  const assessments = assessmentsQuery.data ?? [];
  const decisions = decisionsQuery.data ?? [];
  const latestAssessment = assessments[0];

  const hasFinalDecision = decisions.some(
    (decision) =>
      decision.decision_status === "approved" ||
      decision.decision_status === "rejected",
  );

  const canRunAssessment =
    application?.status === "pending" ||
    application?.status === "assessed";

  const canCreateDecision =
    application?.status !== "approved" &&
    application?.status !== "rejected" &&
    application?.status !== "withdrawn" &&
    !hasFinalDecision;

  const handleRunAssessment = () => {
    if (!id || !canRunAssessment || runAssessment.isPending) {
      return;
    }

    runAssessment.mutate(id);
  };

  const handleCreateDecision = (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!id || !canCreateDecision || createDecision.isPending) {
      return;
    }

    createDecision.mutate(
      {
        application_id: id,
        assessment_id: latestAssessment?.id ?? null,
        decision_status: decisionStatus,
        reason: decisionReason.trim() || null,
      },
      {
        onSuccess: () => {
          setDecisionReason("");
          setDecisionStatus("manual_review");
        },
      },
    );
  };

  if (applicationQuery.isLoading) {
    return (
      <div className="text-sm text-muted-foreground">
        Loading application...
      </div>
    );
  }

  if (applicationQuery.isError || !application) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">
          Failed to load application:{" "}
          {applicationQuery.error?.message ?? "Application not found"}
        </p>

        <button
          onClick={() => navigate("/applications")}
          className="text-sm text-primary hover:underline"
        >
          Back to Applications
        </button>
      </div>
    );
  }

  const features = latestAssessment?.features ?? {};

  const dti = getFeatureNumber(features, "debt_to_income_ratio");
  const loanToIncome = getFeatureNumber(
    features,
    "loan_to_monthly_income_ratio",
  );
  const estimatedPayment = getFeatureNumber(
    features,
    "estimated_monthly_payment",
  );

  const isCalibrated =
    features.probability_of_default_is_calibrated === true;

  return (
    <div className="space-y-8">
      <button
        onClick={() => navigate("/applications")}
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Back to Applications
      </button>

      <div className="flex items-center gap-3">
        <div className="flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <FileText className="size-6" />
        </div>

        <div>
          <h1 className="text-2xl font-semibold text-foreground">
            Credit Application
          </h1>
          <p className="font-mono text-xs text-muted-foreground">
            {application.id}
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-border bg-card p-6">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-base font-semibold text-foreground">
            Application Information
          </h2>

          <span
            className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${statusStyles[application.status]}`}
          >
            {application.status.replace("_", " ")}
          </span>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <p className="text-xs text-muted-foreground">Loan Amount</p>
            <p className="mt-1 text-lg font-semibold text-foreground">
              {Number(application.requested_amount).toLocaleString("en-US", {
                style: "currency",
                currency: application.currency_code,
              })}
            </p>
          </div>

          <div>
            <p className="text-xs text-muted-foreground">Loan Term</p>
            <p className="mt-1 text-sm text-foreground">
              {application.term_months} months
            </p>
          </div>

          <div>
            <p className="text-xs text-muted-foreground">Purpose</p>
            <p className="mt-1 text-sm text-foreground">
              {application.purpose}
            </p>
          </div>

          <div>
            <p className="text-xs text-muted-foreground">Created</p>
            <p className="mt-1 text-sm text-foreground">
              {new Date(application.created_at).toLocaleString("en-US")}
            </p>
          </div>

          <div>
            <p className="text-xs text-muted-foreground">Last Updated</p>
            <p className="mt-1 text-sm text-foreground">
              {new Date(application.updated_at).toLocaleString("en-US")}
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-base font-semibold text-foreground">
          Customer
        </h2>

        {customerQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">
            Loading customer...
          </p>
        ) : customerQuery.data ? (
          <button
            onClick={() =>
              navigate(`/customers/${customerQuery.data.id}`)
            }
            className="text-left"
          >
            <p className="text-sm font-medium text-primary hover:underline">
              {customerQuery.data.full_name}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {customerQuery.data.email ?? "No email provided"}
            </p>
          </button>
        ) : (
          <p className="text-sm text-muted-foreground">
            Customer information unavailable.
          </p>
        )}
      </section>

      <section className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Credit Scoring
            </h2>
            <p className="text-sm text-muted-foreground">
              Run a rule-based credit assessment for this application.
            </p>
          </div>

          {canRunAssessment && (
            <button
              onClick={handleRunAssessment}
              disabled={runAssessment.isPending}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {runAssessment.isPending ? (
                <LoaderCircle className="size-4 animate-spin" />
              ) : (
                <Play className="size-4" />
              )}
              {runAssessment.isPending
                ? "Running Assessment..."
                : "Run Credit Assessment"}
            </button>
          )}
        </div>

        {runAssessment.isError && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
            Failed to run assessment: {runAssessment.error.message}
          </div>
        )}

        {assessmentsQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">
            Loading assessment results...
          </p>
        ) : assessmentsQuery.isError ? (
          <p className="text-sm text-destructive">
            Failed to load assessment results.
          </p>
        ) : latestAssessment ? (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-border bg-card p-5">
                <p className="text-xs text-muted-foreground">
                  Credit Score
                </p>
                <p className="mt-2 text-3xl font-semibold text-foreground">
                  {latestAssessment.credit_score}
                  <span className="ml-1 text-sm font-normal text-muted-foreground">
                    / 850
                  </span>
                </p>
              </div>

              <div className="rounded-xl border border-border bg-card p-5">
                <p className="text-xs text-muted-foreground">
                  Risk Indicator
                </p>
                <p className="mt-2 text-3xl font-semibold text-foreground">
                  {(Number(latestAssessment.probability_of_default) * 100).toFixed(2)}%
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {isCalibrated
                    ? "Calibrated probability"
                    : "Uncalibrated estimate"}
                </p>
              </div>

              <div className="rounded-xl border border-border bg-card p-5">
                <p className="text-xs text-muted-foreground">
                  Debt-to-Income Ratio
                </p>
                <p className="mt-2 text-3xl font-semibold text-foreground">
                  {dti !== null ? `${(dti * 100).toFixed(2)}%` : "—"}
                </p>
              </div>

              <div className="rounded-xl border border-border bg-card p-5">
                <p className="text-xs text-muted-foreground">
                  Loan-to-Income Ratio
                </p>
                <p className="mt-2 text-3xl font-semibold text-foreground">
                  {loanToIncome !== null
                    ? `${loanToIncome.toFixed(2)}x`
                    : "—"}
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-5">
              <h3 className="text-sm font-semibold text-foreground">
                Assessment Details
              </h3>

              <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Estimated Monthly Payment
                  </p>
                  <p className="mt-1 text-sm font-medium text-foreground">
                    {estimatedPayment !== null
                      ? estimatedPayment.toLocaleString("en-US", {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })
                      : "—"}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">Model</p>
                  <p className="mt-1 text-sm font-medium text-foreground">
                    {latestAssessment.model_name} v
                    {latestAssessment.model_version}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-muted-foreground">
                    Evaluated At
                  </p>
                  <p className="mt-1 text-sm font-medium text-foreground">
                    {new Date(
                      latestAssessment.evaluated_at,
                    ).toLocaleString("en-US")}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-700 dark:text-amber-400">
              This is a demonstration rule-based scoring model. The risk
              indicator is not a calibrated probability of default. Estimated
              monthly payment uses principal only and excludes interest.
            </div>
          </>
        ) : (
          <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No assessment has been performed yet.
          </div>
        )}
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Assessment History
          </h2>
          <p className="text-sm text-muted-foreground">
            Previous assessments for this application.
          </p>
        </div>

        {assessmentsQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">
            Loading assessments...
          </p>
        ) : assessmentsQuery.isError ? (
          <p className="text-sm text-destructive">
            Failed to load assessments.
          </p>
        ) : assessments.length ? (
          <div className="overflow-x-auto rounded-xl border border-border bg-card">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-6 py-4">Credit Score</th>
                  <th className="px-6 py-4">Risk Indicator</th>
                  <th className="px-6 py-4">Model</th>
                  <th className="px-6 py-4">Evaluated At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {assessments.map((assessment) => (
                  <tr key={assessment.id}>
                    <td className="px-6 py-4 font-semibold text-foreground">
                      {assessment.credit_score}
                    </td>
                    <td className="px-6 py-4 text-foreground">
                      {(Number(assessment.probability_of_default) * 100).toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {assessment.model_name} v{assessment.model_version}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {new Date(assessment.evaluated_at).toLocaleString("en-US")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No assessments found.
          </div>
        )}
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Create Credit Decision
          </h2>
          <p className="text-sm text-muted-foreground">
            Record a decision for this credit application.
          </p>
        </div>

        {!canCreateDecision ? (
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="flex items-center gap-2 text-sm font-medium text-foreground">
              <CheckCircle2 className="size-4 text-green-600" />
              Final decision recorded
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              This application already has a final decision. No further
              decisions can be created.
            </p>
          </div>
        ) : (
          <form
            onSubmit={handleCreateDecision}
            className="space-y-4 rounded-xl border border-border bg-card p-6"
          >
            <div>
              <label
                htmlFor="decision-status"
                className="mb-2 block text-sm font-medium text-foreground"
              >
                Decision
              </label>
              <select
                id="decision-status"
                value={decisionStatus}
                onChange={(event) =>
                  setDecisionStatus(event.target.value as DecisionStatus)
                }
                disabled={createDecision.isPending}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none focus:border-primary"
              >
                <option value="manual_review">Manual Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <div>
              <label
                htmlFor="decision-reason"
                className="mb-2 block text-sm font-medium text-foreground"
              >
                Reason
              </label>
              <textarea
                id="decision-reason"
                value={decisionReason}
                onChange={(event) => setDecisionReason(event.target.value)}
                disabled={createDecision.isPending}
                rows={3}
                placeholder="Enter the reason for this decision..."
                className="w-full resize-y rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
              />
            </div>

            <div className="text-xs text-muted-foreground">
              {latestAssessment
                ? `The latest assessment (${latestAssessment.credit_score}/850) will be attached to this decision.`
                : "No assessment is available. The decision will be created without an attached assessment."}
            </div>

            {createDecision.isError && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
                Failed to create decision: {createDecision.error.message}
              </div>
            )}

            <button
              type="submit"
              disabled={createDecision.isPending || !canCreateDecision}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {createDecision.isPending && (
                <LoaderCircle className="size-4 animate-spin" />
              )}
              {createDecision.isPending
                ? "Saving Decision..."
                : "Save Decision"}
            </button>
          </form>
        )}
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Decision History
          </h2>
          <p className="text-sm text-muted-foreground">
            Previous decisions for this application.
          </p>
        </div>

        {decisionsQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">
            Loading decisions...
          </p>
        ) : decisionsQuery.isError ? (
          <p className="text-sm text-destructive">
            Failed to load decisions.
          </p>
        ) : decisions.length ? (
          <div className="overflow-x-auto rounded-xl border border-border bg-card">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-6 py-4">Decision</th>
                  <th className="px-6 py-4">Reason</th>
                  <th className="px-6 py-4">Assessment</th>
                  <th className="px-6 py-4">Decided At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {decisions.map((decision) => (
                  <tr key={decision.id}>
                    <td className="px-6 py-4">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${decisionStyles[decision.decision_status]}`}
                      >
                        {decision.decision_status.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {decision.reason ?? "—"}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-muted-foreground">
                      {decision.assessment_id
                        ? decision.assessment_id.slice(0, 8)
                        : "—"}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {new Date(decision.decided_at).toLocaleString("en-US")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No decisions found.
          </div>
        )}
      </section>
    </div>
  );
}
