
import { useState } from "react";

import {
  useCreateCustomer,
  useUpdateCustomer,
} from "../hooks/useCustomers";

import type {
  Customer,
  CustomerCreate,
  CustomerUpdate,
  EmploymentStatus,
} from "@/types/api";

interface CustomerFormProps {
  customer?: Customer;
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface CustomerFormState {
  full_name: string;
  email: string;
  date_of_birth: string;
  monthly_income: string;
  monthly_debt_payments: string;
  employment_months: string;
  employment_status: EmploymentStatus;
}

const inputClassName =
  "h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary";

function getInitialFormData(customer?: Customer): CustomerFormState {
  return {
    full_name: customer?.full_name ?? "",
    email: customer?.email ?? "",
    date_of_birth: customer?.date_of_birth ?? "",
    monthly_income: customer?.monthly_income ?? "",
    monthly_debt_payments: customer?.monthly_debt_payments ?? "",
    employment_months:
      customer?.employment_months?.toString() ?? "",
    employment_status: customer?.employment_status ?? "employed",
  };
}

export function CustomerForm({
  customer,
  onSuccess,
  onCancel,
}: CustomerFormProps) {
  const isEditMode = Boolean(customer);

  const createCustomer = useCreateCustomer();
  const updateCustomer = useUpdateCustomer();

  const mutation = isEditMode ? updateCustomer : createCustomer;

  const [formData, setFormData] = useState<CustomerFormState>(
    () => getInitialFormData(customer),
  );

  function updateField<K extends keyof CustomerFormState>(
    field: K,
    value: CustomerFormState[K],
  ) {
    setFormData((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const financialData = {
      monthly_income: Number(formData.monthly_income),
      monthly_debt_payments: Number(formData.monthly_debt_payments),
      employment_months: Number(formData.employment_months),
      employment_status: formData.employment_status,
    };

    if (isEditMode && customer) {
      const payload: CustomerUpdate = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim() || null,
        date_of_birth: formData.date_of_birth || null,
        ...financialData,
      };

      updateCustomer.mutate(
        {
          id: customer.id,
          data: payload,
        },
        {
          onSuccess: () => onSuccess?.(),
        },
      );

      return;
    }

    const payload: CustomerCreate = {
      full_name: formData.full_name.trim(),
      email: formData.email.trim() || null,
      date_of_birth: formData.date_of_birth || null,
      ...financialData,
    };

    createCustomer.mutate(payload, {
      onSuccess: () => {
        setFormData(getInitialFormData());
        onSuccess?.();
      },
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="space-y-2">
        <label htmlFor="full_name" className="text-sm font-medium text-foreground">
          Full Name
        </label>
        <input
          id="full_name"
          type="text"
          required
          minLength={2}
          maxLength={150}
          value={formData.full_name}
          onChange={(event) => updateField("full_name", event.target.value)}
          placeholder="John Smith"
          className={inputClassName}
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium text-foreground">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(event) => updateField("email", event.target.value)}
          placeholder="john@example.com"
          className={inputClassName}
        />
      </div>

      <div className="space-y-2">
        <label
          htmlFor="date_of_birth"
          className="text-sm font-medium text-foreground"
        >
          Date of Birth
        </label>
        <input
          id="date_of_birth"
          type="date"
          value={formData.date_of_birth}
          onChange={(event) => updateField("date_of_birth", event.target.value)}
          className={inputClassName}
        />
      </div>

      <div className="border-t border-border pt-5">
        <h3 className="text-sm font-semibold text-foreground">
          Financial Information
        </h3>
        <p className="mt-1 text-xs text-muted-foreground">
          Required for credit risk assessment.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label
            htmlFor="monthly_income"
            className="text-sm font-medium text-foreground"
          >
            Monthly Income
          </label>
          <input
            id="monthly_income"
            type="number"
            required
            min="0.01"
            max="9999999999.99"
            step="0.01"
            value={formData.monthly_income}
            onChange={(event) =>
              updateField("monthly_income", event.target.value)
            }
            placeholder="5000.00"
            className={inputClassName}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="monthly_debt_payments"
            className="text-sm font-medium text-foreground"
          >
            Monthly Debt Payments
          </label>
          <input
            id="monthly_debt_payments"
            type="number"
            required
            min="0"
            max="9999999999.99"
            step="0.01"
            value={formData.monthly_debt_payments}
            onChange={(event) =>
              updateField("monthly_debt_payments", event.target.value)
            }
            placeholder="1000.00"
            className={inputClassName}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="employment_months"
            className="text-sm font-medium text-foreground"
          >
            Employment Duration (Months)
          </label>
          <input
            id="employment_months"
            type="number"
            required
            min="0"
            max="1200"
            step="1"
            value={formData.employment_months}
            onChange={(event) =>
              updateField("employment_months", event.target.value)
            }
            placeholder="36"
            className={inputClassName}
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="employment_status"
            className="text-sm font-medium text-foreground"
          >
            Employment Status
          </label>
          <select
            id="employment_status"
            required
            value={formData.employment_status}
            onChange={(event) =>
              updateField(
                "employment_status",
                event.target.value as EmploymentStatus,
              )
            }
            className={inputClassName}
          >
            <option value="employed">Employed</option>
            <option value="self_employed">Self-employed</option>
            <option value="unemployed">Unemployed</option>
            <option value="student">Student</option>
            <option value="retired">Retired</option>
          </select>
        </div>
      </div>

      {mutation.isError && (
        <p className="text-sm text-destructive">
          {isEditMode ? "Failed to update customer: " : "Failed to create customer: "}
          {mutation.error.message}
        </p>
      )}

      <div className="flex justify-end gap-3 border-t border-border pt-4">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted"
          >
            Cancel
          </button>
        )}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending
            ? isEditMode
              ? "Saving..."
              : "Creating..."
            : isEditMode
              ? "Save Changes"
              : "Create Customer"}
        </button>
      </div>
    </form>
  );
}
