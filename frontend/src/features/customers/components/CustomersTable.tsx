
import { useNavigate } from "react-router-dom";
import { useCustomers } from "../hooks/useCustomers";

export function CustomersTable() {
  const navigate = useNavigate();
  const { data: customers, isLoading, isError, error } = useCustomers({
    offset: 0,
    limit: 20,
  });

  if (isLoading) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
        Loading customers...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-destructive/40 bg-card p-6 text-sm text-destructive">
        Failed to load customers: {error.message}
      </div>
    );
  }

  if (!customers?.length) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
        No customers found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border bg-muted/40 text-xs uppercase tracking-wider text-muted-foreground">
            <tr>
              <th className="px-6 py-4 font-medium">Customer</th>
              <th className="px-6 py-4 font-medium">Email</th>
              <th className="px-6 py-4 font-medium">Date of Birth</th>
              <th className="px-6 py-4 font-medium">Created</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-border">
            {customers.map((customer) => (
              <tr
                key={customer.id}
                onClick={() => navigate(`/customers/${customer.id}`)}
                className="cursor-pointer transition-colors hover:bg-muted/40"
              >
                <td className="px-6 py-4 font-medium text-foreground">
                  {customer.full_name}
                </td>
                <td className="px-6 py-4 text-muted-foreground">
                  {customer.email ?? "—"}
                </td>
                <td className="px-6 py-4 text-muted-foreground">
                  {customer.date_of_birth ?? "—"}
                </td>
                <td className="px-6 py-4 text-muted-foreground">
                  {new Date(customer.created_at).toLocaleDateString("en-US")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="border-t border-border px-6 py-3 text-xs text-muted-foreground">
        Showing {customers.length} customers
      </div>
    </div>
  );
}
