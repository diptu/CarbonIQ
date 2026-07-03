import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "IAM Control Center",
  description: "Manage organizational hierarchy and govern global access across CarbonIQ.",
};

const METRICS = [
  { label: "Active Organizations", value: "248", delta: "+12%", barColor: "bg-primary-container", barWidth: "75%" },
  { label: "Total Managed Users", value: "4,201", delta: "+403", barColor: "bg-secondary-container", barWidth: "60%" },
  { label: "API Requests (24h)", value: "1.2M", note: "Peak: 1.8M", barColor: "bg-primary-container", barWidth: "85%" },
];

const TENANTS = [
  { initial: "V", name: "Veridian Energy", plan: "Enterprise", status: "Healthy", region: "AWS Sydney (ap-southeast-2)", assets: "84 Assets" },
  { initial: "E", name: "EcoGrid Solutions", plan: "Enterprise", status: "Isolated", region: "Azure Frankfurt (germanywestcentral)", assets: "Maintenance" },
  { initial: "N", name: "Nexus Climate", plan: "Pro", status: "Healthy", region: "GCP Tokyo", assets: "37 Assets" },
];

const SECURITY_TOGGLES = [
  { label: "MFA Enforcement", note: "All Users", checked: true },
  { label: "IP Whitelisting", note: "Admin Access", checked: false },
  { label: "JWT Token Rotation", note: "24h Interval", checked: true },
];

const ACTIVITY = [
  { icon: "person", iconClass: "bg-primary-container/20 border-primary-container/30 text-primary-fixed-dim", text: "Admin changed role for user david.kim", time: "14 Minutes ago • Security" },
  { icon: "lan", iconClass: "bg-secondary-container/20 border-secondary-container/30 text-secondary-fixed-dim", text: "New Node deployed in Region US-East-1", time: "42 Minutes ago • Infrastructure" },
  { icon: "key", iconClass: "bg-primary-container/20 border-primary-container/30 text-primary-fixed-dim", text: "Root API keys rotated for Nexus Climate", time: "2 Hours ago • Security" },
  { icon: "warning", iconClass: "bg-error/20 border-error/30 text-error", text: "Failed login attempt from 192.168.1.104", time: "3 Hours ago • Alert" },
];

export default function AdminOverviewPage() {
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto w-full">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <h1 className="font-headline-lg text-headline-lg mb-1">
            IAM Control Center
          </h1>
          <div className="flex items-center gap-2 text-on-surface-variant font-label-md">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-container opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary-container" />
            </span>
            System Health:{" "}
            <span className="text-primary-fixed-dim font-bold">
              Operational
            </span>
          </div>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-surface-container-high border border-outline-variant text-on-surface rounded-lg font-label-md flex items-center gap-2 hover:bg-surface-variant transition-colors">
            <span className="material-symbols-outlined text-sm">
              download
            </span>{" "}
            Export Reports
          </button>
          <button className="px-4 py-2 bg-primary-container text-on-primary-container rounded-lg font-label-md font-bold flex items-center gap-2 active:scale-95 transition-transform">
            <span className="material-symbols-outlined text-sm">add</span>{" "}
            Provision Node
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {METRICS.map((metric) => (
          <GlassCard key={metric.label} className="p-6">
            <p className="text-on-surface-variant font-label-sm uppercase tracking-widest mb-2">
              {metric.label}
            </p>
            <div className="flex items-baseline gap-2">
              <span className="font-headline-lg text-headline-lg text-on-surface">
                {metric.value}
              </span>
              <span
                className={
                  metric.delta
                    ? "text-primary-fixed-dim text-xs font-bold"
                    : "text-on-surface-variant text-xs"
                }
              >
                {metric.delta ?? metric.note}
              </span>
            </div>
            <div className="mt-4 h-1 w-full bg-surface-variant rounded-full overflow-hidden">
              <div
                className={`h-full ${metric.barColor}`}
                style={{ width: metric.barWidth }}
              />
            </div>
          </GlassCard>
        ))}
        <GlassCard className="p-6 border-l-4 border-l-primary-fixed-dim">
          <p className="text-on-surface-variant font-label-sm uppercase tracking-widest mb-2">
            Security Alerts
          </p>
          <div className="flex items-baseline gap-2">
            <span className="font-headline-lg text-headline-lg text-primary-fixed-dim">
              0
            </span>
            <span className="material-symbols-outlined text-primary-fixed-dim text-lg">
              verified
            </span>
          </div>
          <p className="text-[10px] text-on-surface-variant mt-4">
            Last checked: Just now
          </p>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 flex flex-col gap-6">
          <GlassCard className="overflow-hidden">
            <div className="p-6 border-b border-outline-variant flex justify-between items-center">
              <h2 className="font-headline-md text-headline-md">
                Organization Management
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left font-body-sm min-w-[640px]">
                <thead className="bg-surface-container-highest/40 text-on-surface-variant font-label-sm uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4">Tenant Name</th>
                    <th className="px-6 py-4">Plan</th>
                    <th className="px-6 py-4">Node Status</th>
                    <th className="px-6 py-4">Region</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/30">
                  {TENANTS.map((tenant) => (
                    <tr
                      key={tenant.name}
                      className="hover:bg-surface-variant/20 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded bg-surface-container-high flex items-center justify-center text-primary-fixed-dim font-bold">
                            {tenant.initial}
                          </div>
                          <span className="font-medium text-on-surface">
                            {tenant.name}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 rounded bg-primary-container/10 text-primary-fixed-dim border border-primary-container/20 text-[10px] font-bold uppercase tracking-tight">
                          {tenant.plan}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div
                          className={`flex items-center gap-1.5 ${
                            tenant.status === "Healthy"
                              ? "text-primary-fixed-dim"
                              : "text-error"
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              tenant.status === "Healthy"
                                ? "bg-primary-container"
                                : "bg-error animate-pulse"
                            }`}
                          />
                          {tenant.status}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-on-surface-variant">
                        {tenant.region} • {tenant.assets}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <span className="material-symbols-outlined text-primary-fixed-dim">
                security
              </span>
              <h2 className="font-headline-md text-headline-md">
                Global Security Settings
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {SECURITY_TOGGLES.map((toggle) => (
                <div
                  key={toggle.label}
                  className="flex items-center justify-between p-4 bg-surface-container-high/40 rounded-lg border border-outline-variant"
                >
                  <div>
                    <p className="font-label-md text-on-surface">
                      {toggle.label}
                    </p>
                    <p className="text-[10px] text-on-surface-variant uppercase">
                      {toggle.note}
                    </p>
                  </div>
                  <div
                    className={`w-11 h-6 rounded-full relative transition-colors ${
                      toggle.checked
                        ? "bg-primary-container"
                        : "bg-surface-variant"
                    }`}
                  >
                    <div
                      className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                        toggle.checked ? "translate-x-5" : "translate-x-1"
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        <aside className="lg:col-span-4 space-y-6">
          <GlassCard className="flex flex-col h-full">
            <div className="p-6 border-b border-outline-variant flex justify-between items-center">
              <h2 className="font-label-md text-on-surface font-bold">
                Recent Administrative Actions
              </h2>
            </div>
            <div className="p-6 space-y-6">
              {ACTIVITY.map((item) => (
                <div key={item.text} className="relative pl-8">
                  <div
                    className={`absolute left-0 top-0 w-6 h-6 rounded-full flex items-center justify-center z-10 border ${item.iconClass}`}
                  >
                    <span className="material-symbols-outlined text-[14px]">
                      {item.icon}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-on-surface mb-1">
                    {item.text}
                  </p>
                  <p className="text-[11px] text-on-surface-variant uppercase font-bold">
                    {item.time}
                  </p>
                </div>
              ))}
            </div>
            <div className="mt-auto p-4 border-t border-outline-variant">
              <button className="w-full py-2 bg-surface-container-high text-on-surface-variant hover:text-on-surface rounded-lg text-sm transition-colors border border-outline-variant">
                View Full Audit History
              </button>
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h3 className="font-label-md text-on-surface font-bold mb-2">
              Compliance Rating
            </h3>
            <div className="flex items-center gap-4">
              <div className="relative w-16 h-16 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    className="text-surface-variant"
                    cx="32"
                    cy="32"
                    fill="transparent"
                    r="28"
                    stroke="currentColor"
                    strokeWidth="6"
                  />
                  <circle
                    className="text-primary-fixed-dim"
                    cx="32"
                    cy="32"
                    fill="transparent"
                    r="28"
                    stroke="currentColor"
                    strokeDasharray="175"
                    strokeDashoffset="35"
                    strokeWidth="6"
                  />
                </svg>
                <span className="absolute text-xs font-bold text-on-surface">
                  82%
                </span>
              </div>
              <div>
                <p className="text-xs text-on-surface-variant mb-1">
                  Current status is{" "}
                  <span className="text-primary-fixed-dim">Elite</span>. You
                  are 18% away from full decentralized compliance.
                </p>
                <a className="text-primary-fixed-dim text-[10px] uppercase font-bold hover:underline" href="#">
                  Improve Score →
                </a>
              </div>
            </div>
          </GlassCard>
        </aside>
      </div>
    </div>
  );
}
