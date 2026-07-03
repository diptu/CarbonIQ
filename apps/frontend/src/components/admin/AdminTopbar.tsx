import Link from "next/link";
import { Logo } from "@/components/ui";

export function AdminTopbar() {
  return (
    <header className="w-full sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-outline-variant/30 shadow-sm flex items-center justify-between px-6 md:px-margin-desktop h-16">
      <Link
        href="/dashboard"
        className="flex items-center gap-2 font-headline-md text-headline-md font-bold text-primary-fixed tracking-tight"
      >
        <Logo size={22} />
        CarbonIQ
      </Link>
      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center bg-surface-container px-3 py-1.5 rounded-lg border border-outline-variant/30">
          <span className="material-symbols-outlined text-on-surface-variant text-[20px]">
            search
          </span>
          <input
            className="bg-transparent border-none focus:ring-0 focus:outline-none text-body-sm font-body-sm placeholder:text-on-surface-variant/50 w-48"
            placeholder="Search tenants..."
            type="text"
          />
        </div>
        <span className="material-symbols-outlined text-on-surface-variant hover:bg-surface-container-highest p-2 rounded-full transition-all cursor-pointer">
          notifications
        </span>
      </div>
    </header>
  );
}
