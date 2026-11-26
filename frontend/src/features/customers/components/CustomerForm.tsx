
import { useState } from "react";
import { useCreateCustomer } from "../hooks/useCustomers";
import type { CustomerCreate } from "@/types/api";

interface CustomerFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CustomerForm({
  onSuccess,
  onCancel,
}: CustomerFormProps) {
  const createCustomer = useCreateCustomer();

  const [formData, setFormData] = useState<CustomerCreate>({
    full_name: "",
    email: "",
    date_of_birth: "",
  });

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    createCustomer.mutate(formData, {
      onSuccess: () => {
        setFormData({
          full_name: "",
          email: "",
          date_of_birth: "",
        });
        onSuccess?.();
      },
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="space-y-2">
        <label
          htmlFor="full_name"
          className="text-sm font-medium text-foreground"
        >
          Full Name
        </label>
        <input
          id="full_name"
          type="text"
          required
          value={formData.full_name}
          onChange={(event) =>
            setFormData({ ...formData, full_name: event.target.value })
          }
          placeholder="John Smith"
          className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary"
        />
      </div>

      <div className="space-y-2">
        <label
          htmlFor="email"
          className="text-sm font-medium text-foreground"
        >
          Email
        </label>
        <input
          id="email"
          type="email"
          value={formData.email ?? ""}
          onChange={(event) =>
            setFormData({ ...formData, email: event.target.value })
          }
          placeholder="john@example.com"
          className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary"
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
          value={formData.date_of_birth ?? ""}
          onChange={(event) =>
            setFormData({
              ...formData,
              date_of_birth: event.target.value,
            })
          }
          className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-colors focus:border-primary"
        />
      </div>

      {createCustomer.isError && (
        <p className="text-sm text-destructive">
          Failed to create customer: {createCustomer.error.message}
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
          disabled={createCustomer.isPending}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {createCustomer.isPending ? "Creating..." : "Create Customer"}
        </button>
      </div>
    </form>
  );
}
