"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/ui";

const NAV_GROUPS = [
  {
    label: null,
    items: [
      { icon: "dashboard", label: "Overview", href: "/dashboard" },
      { icon: "upload_file", label: "Ingestion", href: "/ingestion" },
      { icon: "hub", label: "Integrations", href: "/integrations" },
      { icon: "health_and_safety", label: "Data Health", href: "/data-health" },
      { icon: "psychology", label: "AI Estimation", href: "/ai-estimation" },
      { icon: "bolt", label: "Scope 2", href: "/scope-2" },
      { icon: "eco", label: "Renewables", href: "/renewables-attribution" },
      { icon: "verified_user", label: "Compliance", href: "/compliance/policy-engine" },
      { icon: "query_stats", label: "Analytics", href: "/analytics" },
      { icon: "notifications", label: "Notifications", href: "/notifications" },
    ],
  },
  {
    label: "Ecosystem",
    items: [
      { icon: "fact_check", label: "Verification", href: "/verification/projects" },
      { icon: "storefront", label: "Marketplace", href: "/marketplace" },
      { icon: "route", label: "Credit Lifecycle", href: "/credits/lifecycle" },
      { icon: "account_balance", label: "Governance", href: "/governance" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col fixed left-0 top-0 h-full w-64 bg-surface-container/60 backdrop-blur-2xl py-8 border-r border-white/10 z-50">
      <Link href="/dashboard" className="flex items-center gap-2 px-6 mb-10">
        <Logo size={22} />
        <div>
          <h1 className="font-headline-md text-headline-md font-bold text-primary tracking-tight leading-none">
            CarbonIQ
          </h1>
          <p className="text-[10px] uppercase tracking-widest text-on-surface-variant/60 font-bold mt-1">
            EcoLens Console
          </p>
        </div>
      </Link>
      <nav className="flex-1 space-y-4 px-4 overflow-y-auto">
        {NAV_GROUPS.map((group) => (
          <div key={group.label ?? "primary"} className="space-y-1">
            {group.label && (
              <p className="px-4 pt-3 pb-1 text-[10px] uppercase tracking-widest text-on-surface-variant/40 font-bold">
                {group.label}
              </p>
            )}
            {group.items.map((item) => {
              const active =
                item.href === "/dashboard"
                  ? pathname === "/dashboard"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    active
                      ? "bg-primary/10 text-primary border-r-4 border-primary"
                      : "text-on-surface-variant hover:bg-surface-variant/30 hover:text-on-surface"
                  }`}
                >
                  <span className="material-symbols-outlined text-[20px]">
                    {item.icon}
                  </span>
                  <span className="font-label-md text-label-md">
                    {item.label}
                  </span>
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="mt-auto px-4 pt-6 border-t border-white/5 space-y-4">
        <Link
          href="/onboarding"
          className="w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-3 rounded-lg flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-95 transition-all shadow-[0_0_20px_rgba(0,255,157,0.2)]"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Project
        </Link>
        <Link
          href="/docs"
          className="flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <span className="material-symbols-outlined">help</span>
          <span className="font-label-md text-label-md">Help</span>
        </Link>
      </div>
    </aside>
  );
}
