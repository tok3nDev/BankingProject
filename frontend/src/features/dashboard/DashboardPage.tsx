import { Link } from "react-router-dom";
import {
  Users,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Wallet,
  ArrowRight,
} from "lucide-react";

import { useDashboardStats } from "./hooks/useDashboard";
import type { ApplicationStatus } from "@/types/api";

const statusStyles: Record<ApplicationStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  assessed: "bg-blue-100 text-blue-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  withdrawn: "bg-gray-100 text-gray-700",
};

function formatAmount(amount: string, currency: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number(amount));
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
}

export function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="text-sm text-text-secondary">
        Loading dashboard...
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-red-600">
          Failed to load dashboard statistics.
        </p>
        <button
          onClick={() => refetch()}
          className="text-sm font-medium text-primary hover:underline"
        >
          Try again
        </button>
      </div>
    );
  }

  const stats = [
    {
      label: "Total Customers",
      value: data.total_customers,
      icon: Users,
      color: "text-blue-600 bg-blue-50",
    },
    {
      label: "Total Applications",
      value: data.total_applications,
      icon: FileText,
      color: "text-purple-600 bg-purple-50",
    },
    {
      label: "Pending Applications",
      value: data.pending_applications,
      icon: Clock,
      color: "text-amber-600 bg-amber-50",
    },
    {
      label: "Approved Applications",
      value: data.approved_applications,
      icon: CheckCircle,
      color: "text-green-600 bg-green-50",
    },
    {
      label: "Rejected Applications",
      value: data.rejected_applications,
      icon: XCircle,
      color: "text-red-600 bg-red-50",
    },
  ];

  const statusCounts: {
    status: ApplicationStatus;
    label: string;
    count: number;
  }[] = [
    {
      status: "pending",
      label: "Pending",
      count: data.pending_applications,
    },
    {
      status: "assessed",
      label: "Assessed",
      count: data.assessed_applications,
    },
    {
      status: "approved",
      label: "Approved",
      count: data.approved_applications,
    },
    {
      status: "rejected",
      label: "Rejected",
      count: data.rejected_applications,
    },
    {
      status: "withdrawn",
      label: "Withdrawn",
      count: data.withdrawn_applications,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-text-primary">
          Dashboard
        </h2>
        <p className="mt-1 text-sm text-text-secondary">
          Overview of your banking operations.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {stats.map((stat) => {
          const Icon = stat.icon;

          return (
            <div
              key={stat.label}
              className="rounded-xl border border-border bg-card p-5"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm text-text-secondary">
                  {stat.label}
                </p>
                <div className={`rounded-lg p-2 ${stat.color}`}>
                  <Icon size={18} />
                </div>
              </div>
              <p className="mt-4 text-3xl font-semibold text-text-primary">
                {stat.value}
              </p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-5 flex items-center gap-2">
            <FileText size={18} className="text-text-secondary" />
            <h3 className="font-semibold text-text-primary">
              Application Status
            </h3>
          </div>

          <div className="space-y-4">
            {statusCounts.map((item) => {
              const percentage =
                data.total_applications > 0
                  ? (item.count / data.total_applications) * 100
                  : 0;

              return (
                <div key={item.status}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span className="text-text-secondary">
                      {item.label}
                    </span>
                    <span className="font-medium text-text-primary">
                      {item.count}
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-5 flex items-center gap-2">
            <Wallet size={18} className="text-text-secondary" />
            <h3 className="font-semibold text-text-primary">
              Requested Loan Amount
            </h3>
          </div>

          {data.requested_amount_by_currency.length === 0 ? (
            <p className="text-sm text-text-secondary">
              No applications yet.
            </p>
          ) : (
            <div className="space-y-4">
              {data.requested_amount_by_currency.map((item) => (
                <div
                  key={item.currency_code}
                  className="flex items-center justify-between rounded-lg bg-muted/50 p-4"
                >
                  <span className="text-sm font-medium text-text-secondary">
                    {item.currency_code}
                  </span>
                  <span className="text-xl font-semibold text-text-primary">
                    {formatAmount(
                      item.total_amount,
                      item.currency_code,
                    )}
                  </span>
                </div>
              ))}
            </div>
          )}
          <p className="mt-4 text-xs text-text-secondary">
            Total requested amount across all applications, grouped by currency.
          </p>
        </div>
      </section>

      <section className="overflow-hidden rounded-xl border border-border bg-card">
        <div className="flex items-center justify-between border-b border-border p-5">
          <div>
            <h3 className="font-semibold text-text-primary">
              Recent Applications
            </h3>
            <p className="mt-1 text-sm text-text-secondary">
              Latest five applications.
            </p>
          </div>

          <Link
            to="/applications"
            className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
          >
            View all
            <ArrowRight size={16} />
          </Link>
        </div>

        {data.recent_applications.length === 0 ? (
          <div className="p-8 text-center text-sm text-text-secondary">
            No applications found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-muted/50 text-text-secondary">
                <tr>
                  <th className="px-5 py-3 font-medium">Customer</th>
                  <th className="px-5 py-3 font-medium">Amount</th>
                  <th className="px-5 py-3 font-medium">Purpose</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.recent_applications.map((application) => (
                  <tr
                    key={application.id}
                    className="transition-colors hover:bg-muted/30"
                  >
                    <td className="px-5 py-4">
                      <Link
                        to={`/applications/${application.id}`}
                        className="font-medium text-text-primary hover:text-primary"
                      >
                        {application.customer_name}
                      </Link>
                    </td>
                    <td className="whitespace-nowrap px-5 py-4 text-text-primary">
                      {formatAmount(
                        application.requested_amount,
                        application.currency_code,
                      )}
                    </td>
                    <td className="px-5 py-4 text-text-secondary">
                      {application.purpose}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
                          statusStyles[application.status]
                        }`}
                      >
                        {application.status.replace("_", " ")}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-5 py-4 text-text-secondary">
                      {formatDate(application.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}