import { createBrowserRouter } from "react-router-dom";

import { MainLayout } from "@/components/layout/MainLayout";
import { PlaceholderPage } from "@/components/shared/PlaceholderPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { CustomerDetails } from "@/features/customers/CustomerDetails";
import { CustomersPage } from "@/features/customers/CustomersPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "customers",
        element: <CustomersPage />,
      },
      {
        path: "customers/:id",
        element: <CustomerDetails />,
      },
      {
        path: "applications",
        element: <PlaceholderPage title="Applications" />,
      },
      {
        path: "credit-scoring",
        element: <PlaceholderPage title="Credit Scoring" />,
      },
      {
        path: "decisions",
        element: <PlaceholderPage title="Decisions" />,
      },
      {
        path: "ai-assistant",
        element: <PlaceholderPage title="AI Assistant" />,
      },
      {
        path: "settings",
        element: <PlaceholderPage title="Settings" />,
      },
    ],
  },
]);