
import { Bell, ChevronRight, Search } from "lucide-react";

interface HeaderProps {
  title: string;
}

export function Header({ title }: HeaderProps) {
  return (
    <header className="flex h-20 shrink-0 items-center justify-between border-b border-border bg-background px-8">
      {/* Page title and breadcrumb */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <span>Workspace</span>
          <ChevronRight className="size-3" />
          <span className="text-text-primary">{title}</span>
        </div>

        <h2 className="text-xl font-semibold tracking-tight text-text-primary">
          {title}
        </h2>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative hidden w-64 md:block">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-secondary" />

          <input
            type="text"
            placeholder="Search..."
            className="h-10 w-full rounded-lg border border-border bg-surface pl-9 pr-3 text-sm text-text-primary outline-none transition-colors placeholder:text-text-secondary focus:border-primary"
          />

          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 rounded border border-border px-1.5 py-0.5 text-[10px] text-text-secondary">
            ⌘ K
          </kbd>
        </div>

        {/* Notifications */}
        <button
          type="button"
          aria-label="Notifications"
          className="relative flex size-10 items-center justify-center rounded-lg border border-border bg-surface text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary"
        >
          <Bell className="size-4" />
          <span className="absolute right-2 top-2 size-1.5 rounded-full bg-primary" />
        </button>

        {/* User profile */}
        <div className="flex items-center gap-3 border-l border-border pl-4">
          <div className="flex size-9 items-center justify-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
            A
          </div>

          <div className="hidden flex-col sm:flex">
            <span className="text-sm font-medium text-text-primary">
              Administrator
            </span>
            <span className="text-xs text-text-secondary">
              Credit Analyst
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
