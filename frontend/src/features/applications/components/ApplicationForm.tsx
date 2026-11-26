
import { useState } from "react";

import { useCreateApplication } from "../hooks/useApplications";
import type { ApplicationCreate } from "@/types/api";

interface ApplicationFormProps {
  customerId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export function ApplicationForm({
  customerId,
  onSuccess,
  onCancel,
}: ApplicationFormProps) {
  const createApplication = useCreateApplication();

  const [form, setForm] = useState({
    requested_amount: "",
    currency_code: "USD",
    term_months: "12",
    purpose: "",
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const data: ApplicationCreate = {
      customer_id: customerId,
      requested_amount: Number(form.requested_amount),
      currency_code: form.currency_code,
      term_months: Number(form.term_months),
      purpose: form.purpose.trim(),
    };

    createApplication.mutate(data, {
      onSuccess,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-border bg-surface p-5"
    >
      <h3 className="text-lg font-semibold text-text-primary">
        New Credit Application
      </h3>

      <div>
        <label className="mb-2 block text-sm text-text-secondary">
          Loan Amount
        </label>
        <input
          type="number"
          min="0.01"
          step="0.01"
          required
          value={form.requested_amount}
          onChange={(event) =>
            setForm({ ...form, requested_amount: event.target.value })
          }
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-text-primary"
          placeholder="10000.00"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm text-text-secondary">
          Currency
        </label>
        <select
          value={form.currency_code}
          onChange={(event) =>
            setForm({ ...form, currency_code: event.target.value })
          }
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-text-primary"
        >
          <option value="USD">USD</option>
          <option value="EUR">EUR</option>
          <option value="UAH">UAH</option>
        </select>
      </div>

      <div>
        <label className="mb-2 block text-sm text-text-secondary">
          Loan Term (months)
        </label>
        <input
          type="number"
          min="1"
          max="360"
          required
          value={form.term_months}
          onChange={(event) =>
            setForm({ ...form, term_months: event.target.value })
          }
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-text-primary"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm text-text-secondary">
          Loan Purpose
        </label>
        <input
          type="text"
          minLength={2}
          maxLength={100}
          required
          value={form.purpose}
          onChange={(event) =>
            setForm({ ...form, purpose: event.target.value })
          }
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-text-primary"
          placeholder="Personal loan"
        />
      </div>

      {createApplication.isError && (
        <p className="text-sm text-danger">
          Failed to create application. Check the submitted data and try again.
        </p>
      )}

      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:bg-surface-hover"
        >
          Cancel
        </button>

        <button
          type="submit"
          disabled={createApplication.isPending}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
        >
          {createApplication.isPending ? "Creating..." : "Create Application"}
        </button>
      </div>
    </form>
  );
}
