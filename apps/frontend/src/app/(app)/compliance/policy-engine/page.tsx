import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Compliance & Policy Engine",
  description: "Configure real-time anomaly detection and emission thresholds.",
};

const REPORTS = [
  { icon: "article", title: "Annual ESG Statement", meta: "PDF/XBRL • Verified 2h ago" },
  { icon: "data_object", title: "GHG Protocol Export", meta: "JSON/CSV • Direct API" },
  { icon: "priority_high", title: "Supply Chain Anomaly", meta: "XLSX • 14 unresolved", warn: true },
];

const AUDIT_LOG = [
  { time: "2024-10-24 14:22:01", event: "Threshold Breach Alert", asset: "Node-EM-049 (Berlin)", status: "Critical" },
  { time: "2024-10-24 12:05:44", event: "Policy Update", asset: "Admin System (Global)", status: "Config" },
  { time: "2024-10-24 09:15:30", event: "Automated Report Gen", asset: "CS-Bot-Reporting", status: "Verified" },
  { time: "2024-10-23 23:59:59", event: "Daily Reconciliation", asset: "Consolidated Ledger", status: "Verified" },
];

const STATUS_STYLES: Record<string, string> = {
  Critical: "bg-error/10 text-error border-error/20",
  Config: "bg-secondary-fixed-dim/10 text-secondary-fixed-dim border-secondary-fixed-dim/20",
  Verified: "bg-primary-fixed-dim/10 text-primary-fixed-dim border-primary-fixed-dim/20",
};

const SIMULATION_BARS = [40, 55, 45, 70, 85, 60, 40, 95, 50, 35, 45, 60];

export default function CompliancePolicyEnginePage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-gutter">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="font-headline-xl text-headline-xl text-on-surface">
            Regulatory Compliance
          </h1>
          <p className="text-on-surface-variant font-body-md mt-2 max-w-2xl">
            Manage real-time emission thresholds, immutable audit logs, and
            stakeholder reporting protocols across global microservices.
          </p>
        </div>
        <div className="glass-card p-4 flex items-center gap-4 rounded-xl">
          <div className="w-3 h-3 bg-primary-fixed-dim rounded-full animate-pulse" />
          <span className="font-label-md text-label-md text-primary-fixed-dim">
            System Status: Compliant (v2.4.1)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-gutter">
        {/* Policy engine */}
        <GlassCard className="col-span-12 lg:col-span-8 p-8">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary-fixed-dim p-2 bg-primary-fixed-dim/10 rounded-lg">
                rule_settings
              </span>
              <h3 className="font-headline-md text-headline-md">
                Policy Engine
              </h3>
            </div>
            <div className="flex gap-2">
              <button className="text-label-sm font-label-sm px-3 py-1 bg-white/5 rounded-md text-on-surface-variant border border-white/5">
                Revert
              </button>
              <button className="text-label-sm font-label-sm px-3 py-1 bg-primary-fixed-dim text-on-primary-fixed font-bold rounded-md">
                Update Protocols
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="flex justify-between">
                <label className="font-label-md text-label-md text-on-surface">
                  Scope 1 Emission Limit
                </label>
                <span className="text-primary-fixed-dim font-label-sm">
                  4.2 kt/CO2e
                </span>
              </div>
              <input
                className="w-full h-1.5 bg-surface-container rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim"
                max={100}
                min={0}
                type="range"
                defaultValue={42}
              />
              <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                <p className="text-label-sm font-label-sm text-on-surface-variant mb-2">
                  Anomaly Trigger Action
                </p>
                <select className="w-full bg-transparent border border-white/10 rounded-lg text-body-sm text-on-surface px-3 py-2 focus:border-primary-fixed-dim focus:ring-0 focus:outline-none">
                  <option>Immediate Lockout &amp; Alert</option>
                  <option>Log &amp; Soft Warning</option>
                  <option>Stakeholder Notification</option>
                </select>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex justify-between">
                <label className="font-label-md text-label-md text-on-surface">
                  Energy Intensity Cap
                </label>
                <span className="text-primary-fixed-dim font-label-sm">
                  115 kWh/m²
                </span>
              </div>
              <input
                className="w-full h-1.5 bg-surface-container rounded-lg appearance-none cursor-pointer accent-primary-fixed-dim"
                max={100}
                min={0}
                type="range"
                defaultValue={78}
              />
              <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                <p className="text-label-sm font-label-sm text-on-surface-variant mb-2">
                  Verification Frequency
                </p>
                <div className="flex gap-2">
                  <button className="flex-1 py-1 px-2 rounded bg-primary-fixed-dim text-on-primary-fixed text-label-sm font-bold">
                    Real-time
                  </button>
                  <button className="flex-1 py-1 px-2 rounded bg-white/5 text-on-surface-variant text-label-sm hover:bg-white/10">
                    Hourly
                  </button>
                  <button className="flex-1 py-1 px-2 rounded bg-white/5 text-on-surface-variant text-label-sm hover:bg-white/10">
                    Daily
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/5">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-label-md text-label-md text-on-surface-variant">
                Threshold Simulation (24h Forecast)
              </h4>
              <span className="text-label-sm font-label-sm text-primary-fixed-dim bg-primary-fixed-dim/20 px-2 py-0.5 rounded">
                Safe Margin: 12.4%
              </span>
            </div>
            <div className="h-24 flex items-end gap-1">
              {SIMULATION_BARS.map((h, i) => (
                <div
                  key={i}
                  className={`flex-1 rounded-t-sm transition-all ${
                    h === 95
                      ? "bg-error/40 hover:bg-error"
                      : "bg-primary-fixed-dim/20 hover:bg-primary-fixed-dim"
                  }`}
                  style={{ height: `${h}%` }}
                />
              ))}
            </div>
            <p className="text-label-sm text-on-surface-variant mt-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-error text-[16px]">
                warning
              </span>
              Predicted threshold breach at 04:00 AM based on historical
              load.
            </p>
          </div>
        </GlassCard>

        {/* Reporting center */}
        <GlassCard className="col-span-12 lg:col-span-4 p-8 flex flex-col">
          <div className="flex items-center gap-3 mb-4">
            <span className="material-symbols-outlined text-secondary-container p-2 bg-secondary-container/10 rounded-lg">
              description
            </span>
            <h3 className="font-headline-md text-headline-md">
              Reporting Center
            </h3>
          </div>
          <p className="text-body-sm text-on-surface-variant mb-6">
            Generate certified documentation for ESG auditors and
            stakeholders.
          </p>
          <div className="flex-1 space-y-4">
            {REPORTS.map((report) => (
              <div
                key={report.title}
                className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-primary-fixed-dim/30 transition-all cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-3">
                    <span
                      className={`material-symbols-outlined ${
                        report.warn ? "text-error" : "text-primary-fixed-dim"
                      }`}
                    >
                      {report.icon}
                    </span>
                    <h4 className="font-label-md text-label-md text-on-surface">
                      {report.title}
                    </h4>
                  </div>
                  <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary-fixed-dim">
                    download
                  </span>
                </div>
                <p className="text-xs text-on-surface-variant opacity-60">
                  {report.meta}
                </p>
              </div>
            ))}
          </div>
          <button className="w-full mt-6 py-3 border border-dashed border-white/10 rounded-xl font-label-md text-label-md text-on-surface-variant hover:text-primary-fixed-dim hover:border-primary-fixed-dim transition-all flex items-center justify-center gap-2">
            <span className="material-symbols-outlined">schedule_send</span>
            Schedule Recurring Export
          </button>
        </GlassCard>

        {/* Audit trail */}
        <GlassCard className="col-span-12 p-8">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-tertiary-fixed-dim p-2 bg-tertiary-fixed-dim/10 rounded-lg">
                history_edu
              </span>
              <h3 className="font-headline-md text-headline-md">
                Immutable Audit Trail
              </h3>
            </div>
            <button className="flex items-center gap-2 text-label-sm font-label-sm text-on-surface-variant hover:text-on-surface">
              <span className="material-symbols-outlined text-sm">
                filter_list
              </span>
              Filters
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[720px]">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="pb-4 font-label-sm text-label-sm text-on-surface-variant">
                    Timestamp
                  </th>
                  <th className="pb-4 font-label-sm text-label-sm text-on-surface-variant">
                    Event Type
                  </th>
                  <th className="pb-4 font-label-sm text-label-sm text-on-surface-variant">
                    Originating Asset
                  </th>
                  <th className="pb-4 font-label-sm text-label-sm text-on-surface-variant">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {AUDIT_LOG.map((row) => (
                  <tr
                    key={row.time}
                    className="hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="py-4 font-label-md text-label-md text-on-surface">
                      {row.time}
                    </td>
                    <td className="py-4 font-body-sm text-on-surface">
                      {row.event}
                    </td>
                    <td className="py-4 font-body-sm text-on-surface-variant">
                      {row.asset}
                    </td>
                    <td className="py-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${STATUS_STYLES[row.status]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-8 flex justify-between items-center text-label-sm font-label-sm text-on-surface-variant">
            <p>Showing 4 of 2,841 verified events</p>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-primary-fixed-dim/10 text-primary-fixed-dim rounded-lg border border-primary-fixed-dim/20">
                1
              </button>
              <button className="px-4 py-2 hover:bg-white/5 rounded-lg">
                2
              </button>
              <button className="px-4 py-2 hover:bg-white/5 rounded-lg">
                3
              </button>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
