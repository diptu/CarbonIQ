import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Integration Control Center",
  description: "Monitor bidirectional data flows between telemetry nodes and reporting standards.",
};

const SOURCES = [
  {
    icon: "thermostat",
    color: "text-primary-fixed-dim bg-primary-fixed-dim/10",
    name: "HVAC Telemetry",
    detail: "Edge Node Cluster A-14",
    metricLabel: "Latency",
    metricValue: "12ms",
    status: "Active",
    statusColor: "bg-primary-fixed-dim/10 text-primary-fixed-dim border-primary-fixed-dim/20",
  },
  {
    icon: "corporate_fare",
    color: "text-secondary-fixed-dim bg-secondary-fixed-dim/10",
    name: "SAP/ERP Connector",
    detail: "Enterprise Data Bridge",
    metricLabel: "Latency",
    metricValue: "450ms",
    status: "Syncing",
    statusColor: "bg-secondary-fixed-dim/10 text-secondary-fixed-dim border-secondary-fixed-dim/20",
  },
  {
    icon: "electric_bolt",
    color: "text-tertiary-fixed-dim bg-tertiary-fixed-dim/10",
    name: "Grd-Integrate",
    detail: "Utility Provider API",
    metricLabel: "Latency",
    metricValue: "-- ms",
    status: "Reconnecting",
    statusColor: "bg-tertiary-fixed-dim/10 text-tertiary-fixed-dim border-tertiary-fixed-dim/20",
  },
];

const QUALITY_SEGMENTS = [
  { scope: "Scope 1: Direct Combustion", reliability: "98.4%", width: "98.4%", measured: "100% Measured", estimated: "0% Estimated", color: "bg-primary-fixed-dim" },
  { scope: "Scope 2: Purchased Energy", reliability: "92.1%", width: "92.1%", measured: "85% Measured", estimated: "15% Estimated (ML)", color: "bg-primary-fixed-dim" },
  { scope: "Scope 3: Supply Chain", reliability: "64.5%", width: "64.5%", measured: "12% Measured", estimated: "88% Estimated (ML)", color: "bg-secondary-fixed-dim" },
];

export default function IntegrationsPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-8">
      <section className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <p className="text-primary-fixed-dim font-label-md uppercase tracking-widest mb-2">
            System Core
          </p>
          <h1 className="font-headline-lg text-headline-lg text-on-surface">
            Integration Control Center
          </h1>
          <p className="text-on-surface-variant mt-2 max-w-xl">
            Monitor and manage bidirectional data flows between local
            telemetry nodes and global reporting standards.
          </p>
        </div>
        <div className="flex gap-3">
          <button className="px-5 py-2.5 rounded-full border border-white/10 hover:border-primary-fixed-dim/50 text-label-md transition-all flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">sync</span>{" "}
            Sync Data
          </button>
          <button className="px-5 py-2.5 rounded-full border border-white/10 hover:border-primary-fixed-dim/50 text-label-md transition-all flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">
              download
            </span>{" "}
            Export
          </button>
        </div>
      </section>

      <div className="grid grid-cols-12 gap-gutter">
        {/* Real-time connectivity */}
        <GlassCard className="col-span-12 lg:col-span-8 p-8">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary-fixed-dim">
                sensors
              </span>
              <h3 className="font-headline-md text-headline-md">
                Real-time Connectivity
              </h3>
            </div>
            <div className="flex items-center gap-2 bg-surface-container-lowest px-3 py-1.5 rounded-full border border-white/5">
              <span className="w-2 h-2 rounded-full bg-primary-fixed-dim" />
              <span className="text-label-sm font-label-sm text-primary-fixed-dim">
                All Systems Operational
              </span>
            </div>
          </div>
          <div className="space-y-4">
            {SOURCES.map((source) => (
              <div
                key={source.name}
                className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center ${source.color}`}
                  >
                    <span className="material-symbols-outlined">
                      {source.icon}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-label-md text-on-surface">
                      {source.name}
                    </h4>
                    <p className="text-label-sm text-on-surface-variant">
                      {source.detail}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-6 md:gap-12">
                  <div className="text-right hidden sm:block">
                    <p className="text-label-sm text-on-surface-variant mb-1">
                      {source.metricLabel}
                    </p>
                    <p className="text-label-md text-primary-fixed-dim font-bold">
                      {source.metricValue}
                    </p>
                  </div>
                  <div
                    className={`px-4 py-1.5 rounded-full text-label-sm border ${source.statusColor}`}
                  >
                    {source.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Quality index */}
        <GlassCard className="col-span-12 lg:col-span-4 p-8">
          <div className="flex items-center gap-3 mb-8">
            <span className="material-symbols-outlined text-primary-fixed-dim">
              verified
            </span>
            <h3 className="font-headline-md text-headline-md">
              Quality Index
            </h3>
          </div>
          <div className="space-y-6">
            {QUALITY_SEGMENTS.map((segment) => (
              <div key={segment.scope}>
                <div className="flex justify-between items-end mb-2">
                  <span className="text-label-md font-bold">
                    {segment.scope}
                  </span>
                  <span className="text-label-sm text-primary-fixed-dim font-bold">
                    {segment.reliability} Reliability
                  </span>
                </div>
                <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${segment.color}`}
                    style={{ width: segment.width }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-[10px] text-on-surface-variant uppercase tracking-tighter">
                  <span>{segment.measured}</span>
                  <span>{segment.estimated}</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* API key management */}
        <GlassCard className="col-span-12 lg:col-span-6 p-8">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-primary-fixed-dim">
              key
            </span>
            <h3 className="font-headline-md text-headline-md">
              Ingestion Gateways
            </h3>
          </div>
          <div className="bg-surface-container-lowest rounded-2xl p-6 border border-white/5">
            <div className="flex justify-between items-center mb-4">
              <label className="text-label-sm text-on-surface-variant">
                Energy Meter API Key
              </label>
              <span className="text-[10px] px-2 py-0.5 rounded bg-primary-fixed-dim/20 text-primary-fixed-dim font-bold">
                SECURE
              </span>
            </div>
            <div className="flex gap-3 mb-6">
              <div className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 flex items-center justify-between">
                <code className="text-primary-fixed-dim font-mono text-sm">
                  ••••••••••••••••••••••••••••••
                </code>
                <span className="material-symbols-outlined text-on-surface-variant hover:text-white cursor-pointer">
                  visibility
                </span>
              </div>
              <button className="px-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all">
                <span className="material-symbols-outlined">
                  content_copy
                </span>
              </button>
            </div>
            <div className="flex items-center justify-between text-label-sm">
              <p className="text-on-surface-variant italic">
                Last rotated: 12 days ago
              </p>
              <button className="text-primary-fixed-dim hover:underline font-bold flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">
                  refresh
                </span>{" "}
                Rotate Credentials
              </button>
            </div>
          </div>
        </GlassCard>

        {/* Legacy upload */}
        <GlassCard className="col-span-12 lg:col-span-6 p-8 flex flex-col">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-primary-fixed-dim">
              upload_file
            </span>
            <h3 className="font-headline-md text-headline-md">
              Legacy Data Upload
            </h3>
          </div>
          <div className="flex-1 border-2 border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center p-8 hover:border-primary-fixed-dim/40 transition-all cursor-pointer">
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-3xl text-on-surface-variant">
                cloud_upload
              </span>
            </div>
            <p className="font-label-md text-on-surface mb-1">
              Drag &amp; drop files here
            </p>
            <p className="text-label-sm text-on-surface-variant">
              Supports .CSV, .XLSX, and .JSON (Max 50MB)
            </p>
            <button className="mt-6 px-6 py-2 bg-white/10 hover:bg-white/20 rounded-full text-label-md transition-all">
              Browse System
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
