
import { useState } from "react";
import { Plus, Users } from "lucide-react";

import { CustomersTable } from "./components/CustomersTable";
import { CustomerForm } from "./components/CustomerForm";

export function CustomersPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);

  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <Users className="size-5 text-primary" />
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              Customers
            </h1>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage customer profiles and personal information.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsFormOpen(true)}
          className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-white transition-colors hover:bg-primary/90"
        >
          <Plus className="size-4" />
          Add Customer
        </button>
      </div>

      {isFormOpen && (
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-6">
            <h2 className="text-base font-semibold text-foreground">
              New Customer
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Enter the customer's personal information.
            </p>
          </div>

          <CustomerForm
            onSuccess={() => setIsFormOpen(false)}
            onCancel={() => setIsFormOpen(false)}
          />
        </div>
      )}

      <CustomersTable />
    </div>
  );
}
