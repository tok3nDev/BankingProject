
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Mail,
  CalendarDays,
  UserRound,
  Wallet,
  BriefcaseBusiness,
  Clock,
} from "lucide-react";

import { useCustomer } from "./hooks/useCustomers";
import { useCustomerApplications } from "@/features/applications/hooks/useApplications";
import { ApplicationForm } from "@/features/applications/components/ApplicationForm";

const employmentLabels: Record<string, string> = {
  employed: "Employed",
  self_employed: "Self-employed",
  unemployed: "Unemployed",
  student: "Student",
  retired: "Retired",
};

function formatMoney(value: string | null): string {
  if (value === null) {
    return "Not provided";
  }

  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function CustomerDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: customer,
    isLoading,
    isError,
    error,
  } = useCustomer(id ?? "");

  const {
    data: applications,
    isLoading: isApplicationsLoading,
  } = useCustomerApplications(id ?? "", {
    offset: 0,
    limit: 20,
  });

  const [showApplicationForm, setShowApplicationForm] = useState(false);

  if (isLoading) {
    return (
      <div className="text-sm text-muted-foreground">
        Loading customer...
      </div>
    );
  }

  if (isError || !customer) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">
          Failed to load customer: {error?.message ?? "Customer not found"}
        </p>
        <button
          onClick={() => navigate("/customers")}
          className="text-sm text-primary hover:underline"
        >
          Back to Customers
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <button
        onClick={() => navigate("/customers")}
        className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Back to Customers
      </button>

      <div className="flex items-center gap-3">
        <div className="flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <UserRound className="size-6" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            {customer.full_name}
          </h1>
          <p className="text-sm text-muted-foreground">
            Customer Profile
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="mb-6 text-base font-semibold text-foreground">
          Personal Information
        </h2>

        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <Mail className="size-4" />
              Email
            </div>
            <p className="text-sm text-foreground">
              {customer.email ?? "Not provided"}
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <CalendarDays className="size-4" />
              Date of Birth
            </div>
            <p className="text-sm text-foreground">
              {customer.date_of_birth ?? "Not provided"}
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-6">
        <h2 className="mb-6 text-base font-semibold text-foreground">
          Financial Profile
        </h2>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <Wallet className="size-4" />
              Monthly Income
            </div>
            <p className="text-sm font-medium text-foreground">
              {formatMoney(customer.monthly_income)}
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <Wallet className="size-4" />
              Monthly Debt Payments
            </div>
            <p className="text-sm font-medium text-foreground">
              {formatMoney(customer.monthly_debt_payments)}
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="size-4" />
              Employment Duration
            </div>
            <p className="text-sm font-medium text-foreground">
              {customer.employment_months !== null
                ? `${customer.employment_months} months`
                : "Not provided"}
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
              <BriefcaseBusiness className="size-4" />
              Employment Status
            </div>
            <p className="text-sm font-medium text-foreground">
              {customer.employment_status
                ? employmentLabels[customer.employment_status] ??
                  customer.employment_status
                : "Not provided"}
            </p>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Credit Applications
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Applications associated with this customer.
          </p>
        </div>

        <div className="mb-4 flex justify-end">
          <button
            onClick={() => setShowApplicationForm((current) => !current)}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            {showApplicationForm ? "Close Form" : "New Application"}
          </button>
        </div>

        {showApplicationForm && (
          <div className="mb-6">
            <ApplicationForm
              customerId={customer.id}
              onSuccess={() => setShowApplicationForm(false)}
              onCancel={() => setShowApplicationForm(false)}
            />
          </div>
        )}

        {isApplicationsLoading ? (
          <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            Loading applications...
          </div>
        ) : applications?.length ? (
          <div className="overflow-hidden rounded-xl border border-border bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-border bg-muted/40 text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="px-6 py-4 font-medium">Amount</th>
                    <th className="px-6 py-4 font-medium">Purpose</th>
                    <th className="px-6 py-4 font-medium">Term</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {applications.map((application) => (
                    <tr key={application.id}>
                      <td className="px-6 py-4 text-foreground">
                        {Number(application.requested_amount).toLocaleString(
                          "en-US",
                          {
                            style: "currency",
                            currency: application.currency_code,
                          },
                        )}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {application.purpose}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {application.term_months} months
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {application.status}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {new Date(application.created_at).toLocaleDateString(
                          "en-US",
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No credit applications found.
          </div>
        )}
      </section>
    </div>
  );
}
