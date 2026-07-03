import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Audit Logs",
  description: "System-wide event log for compliance and security review.",
};

const ACTIVITY_BARS = [40, 60, 45, 80, 55, 90, 100];

const SEVERITY_FILTERS = [
  { label: "Critical", count: 12, color: "bg-error-container/30 text-error" },
  { label: "Warning", count: 45, color: "bg-tertiary-container/20 text-tertiary-fixed" },
  { label: "Info", count: "1.2k", color: "bg-primary-container/10 text-primary-container", checked: true },
];

const LOG_ROWS = [
  { time: "2023-10-24 14:32:01", actor: "j.doe@carboniq.io", actorIcon: "person", action: "Credit Minted", resource: "TX_99281_A2", ip: "192.168.1.45", ok: true },
  { time: "2023-10-24 14:30:55", actor: "SYSTEM_CORE", actorIcon: "settings_suggest", action: "Health Check", resource: "SRV_M_01", ip: "LOCAL_0.1", ok: true },
  { time: "2023-10-24 14:28:12", actor: "API_GATEWAY", actorIcon: "warning", action: "API Key Revoked", resource: "KEY_EX_881", ip: "45.2.112.9", ok: false },
  { time: "2023-10-24 14:25:00", actor: "admin_root", actorIcon: "person", action: "Role Changed", resource: "USR_PRO_009", ip: "192.168.1.1", ok: true },
  { time: "2023-10-24 14:22:44", actor: "AuthProxy", actorIcon: "shield", action: "Login Success", resource: "SESS_9921", ip: "88.1.22.4", ok: true },
  { time: "2023-10-24 14:15:10", actor: "m.chen@carboniq.io", actorIcon: "person", action: "Node Deploy", resource: "NODE_UK_2", ip: "192.168.1.102", ok: true },
];

export default function AuditLogsPage() {
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto w-full space-y-8">
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
        <GlassCard className="lg:col-span-2 p-6 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="font-headline-md text-headline-md text-primary-container">
                System Activity
              </h2>
              <p className="text-on-surface-variant text-body-sm">
                Event volume over the last 7 days
              </p>
            </div>
            <div className="text-right">
              <span className="text-headline-lg font-extrabold text-primary">
                14.2k
              </span>
              <p className="text-label-sm text-primary-container flex items-center justify-end gap-1">
                <span className="material-symbols-outlined text-sm">
                  trending_up
                </span>{" "}
                +12%
              </p>
            </div>
          </div>
          <div className="h-24 w-full flex items-end gap-2">
            {ACTIVITY_BARS.map((height, i) => (
              <div
                key={i}
                className={`flex-1 rounded-t-sm transition-all ${
                  height === 100
                    ? "bg-primary-container/40 neon-glow"
                    : "bg-primary-container/20 hover:bg-primary-container/40"
                }`}
                style={{ height: `${height}%` }}
              />
            ))}
          </div>
        </GlassCard>
        <GlassCard className="p-6 flex flex-col justify-center gap-4">
          <div className="flex items-center justify-between">
            <span className="text-label-md text-outline">
              Compliance Status
            </span>
            <div className="w-2 h-2 bg-primary-container rounded-full" />
          </div>
          <div className="space-y-1">
            <h3 className="font-headline-md text-primary">Audit Ready</h3>
            <p className="text-body-sm text-on-surface-variant">
              Last external export: 2h ago
            </p>
          </div>
          <div className="flex gap-3 mt-2">
            <button className="flex-1 py-2 bg-surface-container-highest border border-outline-variant text-on-surface rounded font-label-md hover:bg-outline-variant transition-all flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-sm">
                download
              </span>{" "}
              CSV
            </button>
            <button className="flex-1 py-2 bg-surface-container-highest border border-outline-variant text-on-surface rounded font-label-md hover:bg-outline-variant transition-all flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-sm">
                description
              </span>{" "}
              PDF
            </button>
          </div>
        </GlassCard>
      </section>

      <div className="flex flex-col xl:flex-row gap-gutter items-start">
        <GlassCard className="w-full xl:w-72 p-6 space-y-6 shrink-0 border-l-2 border-l-primary-container">
          <div className="flex items-center justify-between">
            <h4 className="font-label-md font-bold uppercase tracking-widest text-primary-container">
              Filters
            </h4>
            <button className="text-label-sm text-outline hover:text-primary transition-colors">
              Reset
            </button>
          </div>
          <div>
            <label className="text-label-sm text-outline block mb-2">
              Severity
            </label>
            <div className="space-y-2">
              {SEVERITY_FILTERS.map((filter) => (
                <label
                  key={filter.label}
                  className="flex items-center gap-3 cursor-pointer group"
                >
                  <input
                    className="rounded bg-surface-container border-outline-variant text-primary-container focus:ring-primary-container/20"
                    type="checkbox"
                    defaultChecked={filter.checked}
                  />
                  <span className="text-body-sm text-on-surface-variant group-hover:text-primary transition-colors">
                    {filter.label}
                  </span>
                  <span
                    className={`ml-auto px-2 py-0.5 rounded text-[10px] ${filter.color}`}
                  >
                    {filter.count}
                  </span>
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="text-label-sm text-outline block mb-2">
              Date Range
            </label>
            <select className="w-full bg-surface-container-lowest border border-outline-variant rounded p-2 text-body-sm text-on-surface-variant focus:border-primary-container focus:ring-0">
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
              <option>Custom Range</option>
            </select>
          </div>
        </GlassCard>

        <GlassCard className="flex-1 overflow-hidden border border-outline-variant">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[720px]">
              <thead className="bg-surface-container-highest/50 border-b border-outline-variant">
                <tr>
                  <th className="px-6 py-4 font-label-md text-outline uppercase tracking-wider text-[10px]">
                    Timestamp
                  </th>
                  <th className="px-6 py-4 font-label-md text-outline uppercase tracking-wider text-[10px]">
                    Actor
                  </th>
                  <th className="px-6 py-4 font-label-md text-outline uppercase tracking-wider text-[10px]">
                    Action Type
                  </th>
                  <th className="px-6 py-4 font-label-md text-outline uppercase tracking-wider text-[10px]">
                    Resource ID
                  </th>
                  <th className="px-6 py-4 font-label-md text-outline uppercase tracking-wider text-[10px]">
                    IP Address
                  </th>
                  <th className="px-6 py-4 font-label-md text-outline uppercase tracking-wider text-[10px] text-right">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30 font-mono text-sm">
                {LOG_ROWS.map((row) => (
                  <tr
                    key={row.time}
                    className={`hover:bg-white/[0.03] transition-colors ${
                      !row.ok ? "bg-error/5" : ""
                    }`}
                  >
                    <td
                      className={`px-6 py-4 whitespace-nowrap ${
                        row.ok ? "text-on-surface-variant" : "text-error"
                      }`}
                    >
                      {row.time}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span
                          className={`material-symbols-outlined text-base ${
                            row.ok ? "text-primary-container" : "text-error"
                          }`}
                        >
                          {row.actorIcon}
                        </span>
                        <span className="text-on-surface">{row.actor}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded text-[11px] font-bold ${
                          row.ok
                            ? "bg-secondary-container/10 text-secondary"
                            : "bg-error-container/30 text-error"
                        }`}
                      >
                        {row.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-outline truncate max-w-[120px]">
                      {row.resource}
                    </td>
                    <td className="px-6 py-4 text-outline">{row.ip}</td>
                    <td className="px-6 py-4 text-right">
                      <span
                        className={`material-symbols-outlined text-sm ${
                          row.ok ? "text-primary-container" : "text-error"
                        }`}
                      >
                        {row.ok ? "check_circle" : "error"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="bg-surface-container-low px-6 py-4 flex items-center justify-between border-t border-outline-variant">
            <span className="text-body-sm text-on-surface-variant">
              Showing 1-6 of 1,254 events
            </span>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
