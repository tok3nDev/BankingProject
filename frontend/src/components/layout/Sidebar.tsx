
import {
  Activity,
  Bot,
  ChartNoAxesCombined,
  ChevronLeft,
  ClipboardList,
  CreditCard,
  LayoutDashboard,
  Settings,
  Users,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const mainNavigation = [
  {
    title: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Customers",
    path: "/customers",
    icon: Users,
  },
  {
    title: "Applications",
    path: "/applications",
    icon: ClipboardList,
  },
  {
    title: "Credit Scoring",
    path: "/credit-scoring",
    icon: ChartNoAxesCombined,
  },
  {
    title: "Decisions",
    path: "/decisions",
    icon: CreditCard,
  },
];

export function Sidebar() {
  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-border bg-surface px-4 py-5">
      {/* Logo */}
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex size-10 items-center justify-center rounded-xl bg-primary">
          <Activity className="size-5 text-white" />
        </div>

        <div>
          <h1 className="text-sm font-semibold tracking-wide text-text-primary">
            BANKING PROJECT
          </h1>
          <p className="text-xs text-text-secondary">
            Credit Intelligence
          </p>
        </div>
      </div>

      {/* Main navigation */}
      <div className="mb-3 px-3">
        <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-secondary">
          Workspace
        </span>
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {mainNavigation.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-primary/15 font-medium text-primary"
                    : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
                }`
              }
            >
              <Icon className="size-4.5" />
              <span>{item.title}</span>
            </NavLink>
          );
        })}

        {/* AI Assistant */}
        <NavLink
          to="/ai-assistant"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
              isActive
                ? "bg-primary/15 font-medium text-primary"
                : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
            }`
          }
        >
          <Bot className="size-4.5" />
          <span>AI Assistant</span>
          <span className="ml-auto rounded-md border border-border px-1.5 py-0.5 text-[9px] text-text-secondary">
            SOON
          </span>
        </NavLink>
      </nav>

      {/* AI Engine status */}
      <div className="mb-4 rounded-xl border border-border bg-background p-3">
        <div className="mb-2 flex items-center gap-2">
          <span className="size-2 rounded-full bg-amber-500" />
          <span className="text-xs font-medium text-text-primary">
            AI Engine
          </span>
        </div>

        <p className="text-[11px] text-text-secondary">
          Experimental ML
        </p>
      </div>

      {/* Settings */}
      <div className="border-t border-border pt-4">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
              isActive
                ? "bg-primary/15 font-medium text-primary"
                : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
            }`
          }
        >
          <Settings className="size-4.5" />
          <span>Settings</span>
        </NavLink>

        <div className="mt-4 flex items-center justify-between px-3">
          <span className="text-[10px] text-text-secondary">
            Banking Project v0.1
          </span>
          <ChevronLeft className="size-4 text-text-secondary" />
        </div>
      </div>
    </aside>
  );
}
