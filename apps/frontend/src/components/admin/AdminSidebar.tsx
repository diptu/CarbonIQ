"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { icon: "corporate_fare", label: "Organization", href: "/admin" },
  { icon: "group", label: "Users & Roles", href: "/admin/users-roles" },
  { icon: "vpn_key", label: "API & Security", href: "/admin/api-security" },
  { icon: "tune", label: "Settings", href: "/admin/settings" },
  { icon: "receipt_long", label: "Audit Logs", href: "/admin/audit-logs" },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col h-screen w-64 fixed left-0 top-0 bg-surface-container backdrop-blur-xl border-r border-outline-variant/20 py-8 px-4 z-50">
      <div className="mb-8 px-2">
        <div className="flex items-center gap-3 p-3 bg-surface-container-high rounded-xl border border-outline-variant/10">
          <div className="w-10 h-10 bg-primary-fixed-dim rounded-lg flex items-center justify-center">
            <span className="material-symbols-outlined text-on-primary-fixed">
              corporate_fare
            </span>
          </div>
          <div>
            <h3 className="font-headline-sm text-[16px] text-primary-fixed font-bold leading-tight">
              EcoAdmin
            </h3>
            <p className="font-label-sm text-[12px] text-on-surface-variant">
              Enterprise Tier
            </p>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-2">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/admin"
              ? pathname === "/admin"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-150 ${
                active
                  ? "text-primary-fixed bg-primary-container/10 border-r-4 border-primary-fixed font-bold"
                  : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high hover:translate-x-1"
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="font-label-md text-label-md">
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto space-y-2 pt-8 border-t border-outline-variant/10">
        <Link
          href="/dashboard"
          className="w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-3 rounded-lg font-bold active:scale-95 transition-transform mb-6 flex items-center justify-center gap-2"
        >
          <span className="material-symbols-outlined text-[20px]">
            arrow_back
          </span>
          Back to Console
        </Link>
        <Link
          href="/docs"
          className="flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-on-surface transition-all"
        >
          <span className="material-symbols-outlined text-[20px]">
            menu_book
          </span>
          <span className="font-label-md text-label-md">Documentation</span>
        </Link>
      </div>
    </aside>
  );
}
