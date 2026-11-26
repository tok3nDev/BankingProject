import { createBrowserRouter } from "react-router-dom";

import { MainLayout } from "@/components/layout/MainLayout";
import { PlaceholderPage } from "@/components/shared/PlaceholderPage";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { CustomerDetails } from "@/features/customers/CustomerDetails";
import { CustomersPage } from "@/features/customers/CustomersPage";
import { ApplicationsPage } from "@/features/applications/ApplicationsPage";
import { ApplicationDetails } from "@/features/applications/ApplicationDetails";

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
        element: <ApplicationsPage />,
      },
      {
        path: "applications/:id",
        element: <ApplicationDetails />,
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