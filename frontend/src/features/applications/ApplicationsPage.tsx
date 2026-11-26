
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Search } from "lucide-react";

import { useApplications } from "./hooks/useApplications";
import type { ApplicationStatus } from "@/types/api";

const statusOptions: Array<{
  value: ApplicationStatus | "all";
  label: string;
}> = [
  { value: "all", label: "All statuses" },
  { value: "pending", label: "Pending" },
  { value: "assessed", label: "Assessed" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
  { value: "withdrawn", label: "Withdrawn" },
];

const statusStyles: Record<ApplicationStatus, string> = {
  pending: "bg-amber-500/10 text-amber-600",
  assessed: "bg-blue-500/10 text-blue-600",
  approved: "bg-green-500/10 text-green-600",
  rejected: "bg-red-500/10 text-red-600",
  withdrawn: "bg-muted text-muted-foreground",
};

export function ApplicationsPage() {
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<ApplicationStatus | "all">("all");

  const {
    data: applications,
    isLoading,
    isError,
    error,
  } = useApplications({ offset: 0, limit: 100 });

  const filteredApplications = useMemo(() => {
    if (!applications) return [];

    const normalizedSearch = search.trim().toLowerCase();

    return applications.filter((application) => {
      const matchesSearch =
        !normalizedSearch ||
        application.id.toLowerCase().includes(normalizedSearch) ||
        application.customer_id.toLowerCase().includes(normalizedSearch) ||
        application.purpose.toLowerCase().includes(normalizedSearch);

      const matchesStatus =
        statusFilter === "all" || application.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [applications, search, statusFilter]);

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <FileText className="size-5 text-primary" />
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            Applications
          </h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Review and manage credit applications.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-5">
          <p className="text-sm text-muted-foreground">Total applications</p>
          <p className="mt-2 text-2xl font-semibold text-foreground">
            {applications?.length ?? 0}
          </p>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <p className="text-sm text-muted-foreground">Pending</p>
          <p className="mt-2 text-2xl font-semibold text-foreground">
            {applications?.filter((item) => item.status === "pending").length ?? 0}
          </p>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <p className="text-sm text-muted-foreground">Approved</p>
          <p className="mt-2 text-2xl font-semibold text-foreground">
            {applications?.filter((item) => item.status === "approved").length ?? 0}
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by application ID, customer ID or purpose..."
            className="h-10 w-full rounded-lg border border-border bg-card pl-10 pr-3 text-sm text-foreground outline-none focus:border-primary"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value as ApplicationStatus | "all")
          }
          className="h-10 rounded-lg border border-border bg-card px-3 text-sm text-foreground outline-none focus:border-primary"
        >
          {statusOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading && (
        <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
          Loading applications...
        </div>
      )}

      {isError && (
        <div className="rounded-xl border border-destructive/40 bg-card p-6 text-sm text-destructive">
          Failed to load applications: {error.message}
        </div>
      )}

      {!isLoading && !isError && (
        <div className="overflow-hidden rounded-xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border bg-muted/40 text-xs uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-6 py-4 font-medium">Application ID</th>
                  <th className="px-6 py-4 font-medium">Customer ID</th>
                  <th className="px-6 py-4 font-medium">Loan Amount</th>
                  <th className="px-6 py-4 font-medium">Term</th>
                  <th className="px-6 py-4 font-medium">Purpose</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Created</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-border">
                {filteredApplications.map((application) => (
                  <tr
                    key={application.id}
                    onClick={() =>
                      navigate(`/applications/${application.id}`)
                    }
                    className="cursor-pointer transition-colors hover:bg-muted/40"
                  >
                    <td className="px-6 py-4 font-mono text-xs text-foreground">
                      {application.id.slice(0, 8)}
                    </td>

                    <td className="px-6 py-4 font-mono text-xs text-muted-foreground">
                      {application.customer_id.slice(0, 8)}
                    </td>

                    <td className="px-6 py-4 font-medium text-foreground">
                      {Number(application.requested_amount).toLocaleString(
                        "en-US",
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        },
                      )}{" "}
                      {application.currency_code}
                    </td>

                    <td className="px-6 py-4 text-muted-foreground">
                      {application.term_months} months
                    </td>

                    <td className="px-6 py-4 text-muted-foreground">
                      {application.purpose}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusStyles[application.status]}`}
                      >
                        {application.status.replace("_", " ")}
                      </span>
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

          {filteredApplications.length === 0 && (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No applications match your search.
            </div>
          )}

          <div className="border-t border-border px-6 py-3 text-xs text-muted-foreground">
            Showing {filteredApplications.length} of {applications?.length ?? 0} applications
          </div>
        </div>
      )}
    </div>
  );
}
