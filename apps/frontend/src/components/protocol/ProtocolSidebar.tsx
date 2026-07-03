import Link from "next/link";
import { Logo } from "@/components/ui";

const NAV_ITEMS = [
  { icon: "dashboard", label: "Dashboard", href: "/dashboard" },
  { icon: "security", label: "Protocols", href: "/protocol/specifications", active: true },
  { icon: "verified_user", label: "Verification", href: "/verification/projects" },
  { icon: "account_balance_wallet", label: "Registry", href: "/credits/lifecycle" },
  { icon: "query_stats", label: "Analytics", href: "/analytics" },
];

export function ProtocolSidebar() {
  return (
    <aside className="hidden lg:flex flex-col h-screen w-64 fixed left-0 top-0 bg-surface-container-lowest/60 backdrop-blur-xl border-r border-outline-variant/20 py-8 px-4 gap-6 z-50">
      <Link href="/" className="flex items-center gap-3 px-2 mb-4">
        <div className="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center text-on-primary">
          <Logo size={20} />
        </div>
        <div>
          <h2 className="font-headline-md text-headline-md text-primary-fixed-dim leading-none">
            CarbonIQ
          </h2>
          <p className="text-xs text-on-surface-variant font-label-sm tracking-wider uppercase">
            Mainnet
          </p>
        </div>
      </Link>
      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              item.active
                ? "bg-primary-container/10 text-primary-fixed-dim border-r-2 border-primary-fixed-dim"
                : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40"
            }`}
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span className="font-label-md text-label-md">{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="mt-auto pt-6 border-t border-outline-variant/20 space-y-1">
        <Link
          href="/docs"
          className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:text-on-surface transition-all"
        >
          <span className="material-symbols-outlined">description</span>
          <span className="font-label-md text-label-md">Documentation</span>
        </Link>
      </div>
    </aside>
  );
}
