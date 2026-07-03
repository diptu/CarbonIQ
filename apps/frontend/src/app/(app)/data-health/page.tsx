import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Data Health & Lineage",
  description: "Precision monitoring of data integrity, confidence, and lineage.",
};

const CONNECTIONS = [
  {
    icon: "thermostat",
    name: "HVAC Telemetry Sensors",
    detail: "Edge Device Cluster 04-A",
    metricLabel: "Latency",
    metricValue: "12ms",
    metricColor: "text-primary-fixed-dim",
    barWidth: "w-full",
    barColor: "bg-primary-fixed-dim",
    statusIcon: "check_circle",
    statusColor: "text-primary-fixed-dim",
  },
  {
    icon: "database",
    name: "SAP/ERP Connector",
    detail: "Financial Ledger Sync",
    metricLabel: "Last Sync",
    metricValue: "2m ago",
    metricColor: "text-secondary-fixed-dim",
    barWidth: "w-3/4",
    barColor: "bg-secondary-fixed-dim",
    statusIcon: "sync",
    statusColor: "text-secondary-fixed-dim",
  },
  {
    icon: "cloud_sync",
    name: "Grd-Integrate API",
    detail: "External Utility Pricing Feed",
    metricLabel: "Status",
    metricValue: "Reconnecting",
    metricColor: "text-error",
    barWidth: "w-1/4",
    barColor: "bg-error",
    statusIcon: "warning",
    statusColor: "text-error",
  },
];

export default function DataHealthPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-gutter">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <p className="text-primary-fixed-dim font-label-md text-label-md mb-2 tracking-widest uppercase">
            System Integrity Dashboard
          </p>
          <h1 className="font-headline-xl text-headline-xl">
            Precision Monitoring
          </h1>
        </div>
        <div className="flex gap-3">
          <button className="px-6 py-2.5 rounded-full border border-white/10 hover:border-primary-fixed-dim font-label-md text-label-md transition-all">
            Export Logs
          </button>
          <button className="px-6 py-2.5 rounded-full bg-primary-fixed-dim text-on-primary-fixed font-bold font-label-md text-label-md hover:shadow-[0_0_15px_rgba(0,227,139,0.4)] transition-all">
            Sync All Data
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-gutter">
        {/* Live connection hub */}
        <GlassCard className="col-span-12 lg:col-span-8 p-8 neon-glow">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary-fixed-dim text-3xl">
                sensors
              </span>
              <h3 className="font-headline-md text-headline-md">
                Live Connection Hub
              </h3>
            </div>
            <span className="bg-primary-fixed-dim/10 text-primary-fixed-dim px-3 py-1 rounded-full text-label-sm font-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary-fixed-dim animate-pulse" />
              98.4% System Uptime
            </span>
          </div>
          <div className="space-y-4">
            {CONNECTIONS.map((conn) => (
              <div
                key={conn.name}
                className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/5 hover:border-white/20 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center">
                    <span className="material-symbols-outlined text-primary-fixed-dim">
                      {conn.icon}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-label-md text-label-md font-bold">
                      {conn.name}
                    </h4>
                    <p className="text-label-sm text-on-surface-variant">
                      {conn.detail}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 md:gap-8">
                  <div className="text-right hidden sm:block">
                    <p className="text-label-sm text-on-surface-variant">
                      {conn.metricLabel}
                    </p>
                    <p className={`font-label-md text-label-md ${conn.metricColor}`}>
                      {conn.metricValue}
                    </p>
                  </div>
                  <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden hidden md:block">
                    <div className={`h-full ${conn.barWidth} ${conn.barColor}`} />
                  </div>
                  <span
                    className={`material-symbols-outlined ${conn.statusColor}`}
                  >
                    {conn.statusIcon}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Confidence score gauge */}
        <GlassCard className="col-span-12 lg:col-span-4 p-8 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <span className="material-symbols-outlined text-primary-fixed-dim">
                verified
              </span>
              <h3 className="font-headline-md text-headline-md">
                Confidence Score
              </h3>
            </div>
            <div className="relative flex justify-center items-center py-8">
              <svg className="w-48 h-48 transform -rotate-90">
                <circle
                  className="text-white/5"
                  cx="96"
                  cy="96"
                  fill="transparent"
                  r="88"
                  stroke="currentColor"
                  strokeWidth="12"
                />
                <circle
                  className="text-primary-fixed-dim"
                  cx="96"
                  cy="96"
                  fill="transparent"
                  r="88"
                  stroke="currentColor"
                  strokeDasharray="552.92"
                  strokeDashoffset="66.35"
                  strokeWidth="12"
                />
              </svg>
              <div className="absolute text-center">
                <span className="text-4xl font-bold font-headline-xl">
                  88%
                </span>
                <p className="text-label-sm text-on-surface-variant uppercase tracking-widest">
                  Global Integrity
                </p>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center text-label-sm">
              <span className="text-primary-fixed-dim flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-primary-fixed-dim" />{" "}
                Measured
              </span>
              <span className="text-white">74.2 GWh</span>
            </div>
            <div className="flex justify-between items-center text-label-sm">
              <span className="text-on-surface-variant flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-white/20" />{" "}
                Estimated (ML)
              </span>
              <span className="text-white">10.8 GWh</span>
            </div>
            <div className="pt-4 border-t border-white/5">
              <p className="text-label-sm text-on-surface-variant italic">
                &quot;Data integrity remains high. 12% reliance on estimation
                models for missing grid pulses.&quot;
              </p>
            </div>
          </div>
        </GlassCard>

        {/* Input management */}
        <GlassCard className="col-span-12 p-8">
          <div className="flex flex-col md:flex-row gap-12">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-8">
                <span className="material-symbols-outlined text-primary-fixed-dim">
                  key
                </span>
                <h3 className="font-headline-md text-headline-md">
                  Credential Management
                </h3>
              </div>
              <div className="space-y-6">
                <div>
                  <label className="block text-label-sm text-on-surface-variant mb-2">
                    Energy Meter API Gateway
                  </label>
                  <div className="relative">
                    <input
                      className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:border-primary-fixed-dim focus:ring-0 focus:outline-none transition-all font-mono text-sm"
                      type="password"
                      defaultValue="************************"
                      readOnly
                    />
                    <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-white cursor-pointer">
                      visibility
                    </span>
                  </div>
                </div>
                <div className="flex gap-4">
                  <button className="flex-1 py-3 bg-white/5 border border-white/10 rounded-lg font-label-md text-label-md hover:bg-white/10 transition-all">
                    Rotate Keys
                  </button>
                  <button className="flex-1 py-3 bg-white/5 border border-white/10 rounded-lg font-label-md text-label-md hover:bg-white/10 transition-all">
                    View Permissions
                  </button>
                </div>
              </div>
            </div>
            <div className="hidden md:block w-[1px] bg-white/5" />
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-8">
                <span className="material-symbols-outlined text-primary-fixed-dim">
                  upload_file
                </span>
                <h3 className="font-headline-md text-headline-md">
                  Ingest Legacy Data
                </h3>
              </div>
              <div className="border-2 border-dashed border-white/10 rounded-xl p-8 flex flex-col items-center justify-center gap-4 hover:border-primary-fixed-dim/40 transition-all cursor-pointer bg-white/[0.02]">
                <div className="w-16 h-16 rounded-full bg-primary-container/10 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary-fixed-dim text-3xl">
                    cloud_upload
                  </span>
                </div>
                <div className="text-center">
                  <p className="font-label-md text-label-md font-bold mb-1">
                    Bulk CSV / XLSX Dropzone
                  </p>
                  <p className="text-label-sm text-on-surface-variant">
                    Maximum file size 500MB per batch
                  </p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-white/5 rounded-full text-[10px] text-on-surface-variant uppercase font-bold border border-white/5">
                    ISO-8601 Ready
                  </span>
                  <span className="px-3 py-1 bg-white/5 rounded-full text-[10px] text-on-surface-variant uppercase font-bold border border-white/5">
                    Auto-Validation
                  </span>
                </div>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Architecture visualization */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
        <GlassCard className="p-8 relative overflow-hidden">
          <span className="material-symbols-outlined absolute top-0 right-0 p-4 text-8xl opacity-10">
            account_tree
          </span>
          <h4 className="font-headline-md text-headline-md mb-2">
            Lineage Map
          </h4>
          <p className="text-body-sm text-on-surface-variant mb-6">
            Trace every data point from its sensor origin to the final
            executive report.
          </p>
          <button className="flex items-center gap-2 text-primary-fixed-dim font-bold">
            Launch Visualizer{" "}
            <span className="material-symbols-outlined">arrow_forward</span>
          </button>
        </GlassCard>
        <GlassCard className="p-8 md:col-span-2 flex flex-col justify-center">
          <h4 className="font-headline-md text-headline-md mb-2">
            Protocol: V2.4 Stable
          </h4>
          <p className="text-body-sm text-on-surface-variant mb-4">
            Engineering-grade transparency. All data segments are
            hash-verified for immutable audit trails.
          </p>
          <div className="flex gap-4">
            <div className="px-4 py-2 bg-white/5 rounded border border-white/10">
              <p className="text-[10px] text-on-surface-variant uppercase">
                Primary Ledger
              </p>
              <p className="font-mono text-xs text-primary-fixed-dim">
                0x882A...F31C
              </p>
            </div>
            <div className="px-4 py-2 bg-white/5 rounded border border-white/10">
              <p className="text-[10px] text-on-surface-variant uppercase">
                Validator
              </p>
              <p className="font-mono text-xs text-secondary-fixed-dim">
                EcoLens-Node-01
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
