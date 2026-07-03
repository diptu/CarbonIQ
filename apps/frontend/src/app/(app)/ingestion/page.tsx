import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Data Ingestion Hub",
  description: "AI-driven utility data processing and normalization.",
};

const UPLOAD_SOURCES = [
  { icon: "electric_meter", label: "Smart Meters" },
  { icon: "receipt_long", label: "Utility Bills" },
  { icon: "precision_manufacturing", label: "IoT Sensors" },
];

const ACTIVE_INGESTIONS = [
  { icon: "picture_as_pdf", name: "Utility_Jan24.pdf", stage: "OCR Extraction", progress: "82%", color: "text-red-400 bg-red-500/10" },
  { icon: "database", name: "Sensor_Array_X.csv", stage: "Cleaning Data", progress: "45%", color: "text-blue-400 bg-blue-500/10" },
  { icon: "electric_bolt", name: "Meter_Live_Feed", stage: "Syncing", progress: "Live", color: "text-green-400 bg-green-500/10", live: true },
  { icon: "model_training", name: "Historical_Fill.json", stage: "AI Inference", progress: "12%", color: "text-yellow-400 bg-yellow-500/10" },
];

const RECENT_ROWS = [
  { source: "Tesla Giga Berlin", type: "Industrial IoT", period: "Dec 2023", confidence: "99.8%", status: "Verified", dot: "bg-primary" },
  { source: "Amsterdam Office", type: "Smart Meter", period: "Q4 2023", confidence: "96.5%", status: "In Progress", dot: "bg-secondary" },
  { source: "Fleet Logistics V2", type: "CSV Manual", period: "Nov 2023", confidence: "88.2%", status: "Manual Review", dot: "bg-yellow-500" },
  { source: "Data Center Alpha", type: "API Endpoint", period: "Real-time", confidence: "99.9%", status: "Verified", dot: "bg-primary" },
];

const STATUS_STYLES: Record<string, string> = {
  Verified: "bg-primary/10 text-primary border-primary/20",
  "In Progress": "bg-secondary/10 text-secondary border-secondary/20",
  "Manual Review": "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
};

export default function IngestionPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-10">
      <section className="space-y-2">
        <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight">
          Data Ingestion Hub
        </h1>
        <p className="text-on-surface-variant text-body-lg max-w-2xl">
          High-integrity, AI-driven utility data processing. Harnessing
          advanced neural networks to infer missing metrics and normalize
          multi-source carbon footprints.
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        {/* Upload area */}
        <GlassCard className="lg:col-span-8 p-8 flex flex-col items-center justify-center border-dashed border-2 border-primary/20 min-h-[400px]">
          <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-6">
            <span className="material-symbols-outlined text-primary text-4xl">
              cloud_upload
            </span>
          </div>
          <h3 className="font-headline-md text-headline-md mb-2">
            Drop your data here
          </h3>
          <p className="text-on-surface-variant mb-8 text-center max-w-md">
            Supported formats: CSV, PDF, XLS, and direct Smart Meter JSON
            streams. Max file size 256MB.
          </p>
          <div className="flex gap-4">
            <button className="bg-primary-container text-on-primary-container px-8 py-3 rounded-xl font-label-md neon-glow hover:opacity-90 transition-all">
              Browse Files
            </button>
            <button className="bg-surface-container-highest text-on-surface px-8 py-3 rounded-xl font-label-md border border-white/5 hover:bg-white/10 transition-all">
              Connect API
            </button>
          </div>
          <div className="mt-12 grid grid-cols-3 gap-8 w-full border-t border-white/5 pt-8">
            {UPLOAD_SOURCES.map((source) => (
              <div key={source.label} className="text-center">
                <span className="material-symbols-outlined text-secondary mb-2 block">
                  {source.icon}
                </span>
                <p className="text-xs text-on-surface-variant uppercase tracking-tighter">
                  {source.label}
                </p>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* AI insights */}
        <div className="lg:col-span-4 space-y-gutter">
          <GlassCard className="p-6 border-l-4 border-l-primary-container">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-label-md text-label-md uppercase tracking-wider text-primary">
                AI Insights
              </h3>
              <span className="material-symbols-outlined text-primary-container">
                neurology
              </span>
            </div>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-end mb-2">
                  <p className="text-on-surface-variant text-sm">
                    Data Gaps Filled
                  </p>
                  <p className="text-primary font-bold text-lg">14 pts</p>
                </div>
                <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary/40 to-primary-container w-[98%]" />
                </div>
                <p className="text-[11px] text-on-surface-variant mt-2">
                  Inferred with 98.4% historical accuracy
                </p>
              </div>
              <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                <p className="text-xs text-on-surface-variant uppercase mb-3">
                  Inferred Load Profiles
                </p>
                <div className="flex items-end gap-1 h-12">
                  {[30, 45, 80, 60, 100, 70, 40].map((h, i) => (
                    <div
                      key={i}
                      className={`flex-1 rounded-t-sm ${
                        h === 100 ? "bg-primary-container" : "bg-primary/40"
                      }`}
                      style={{ height: `${h}%` }}
                    />
                  ))}
                </div>
                <p className="text-[10px] text-secondary mt-3 flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">
                    trending_up
                  </span>
                  Peak demand predicted for 14:00 UTC
                </p>
              </div>
            </div>
          </GlassCard>
          <GlassCard className="p-6">
            <h4 className="font-label-md text-label-md mb-4 text-on-surface">
              Compliance Guard
            </h4>
            <div className="flex items-start gap-3">
              <div className="p-2 bg-secondary/10 rounded-lg">
                <span className="material-symbols-outlined text-secondary text-xl">
                  gavel
                </span>
              </div>
              <p className="text-sm text-on-surface-variant">
                All processed data automatically maps to{" "}
                <span className="text-on-surface font-medium">
                  GHG Protocol Scope 2
                </span>{" "}
                standards.
              </p>
            </div>
          </GlassCard>
        </div>

        {/* Active ingestions */}
        <div className="lg:col-span-12 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-headline-md text-headline-md">
              Active Ingestions
            </h3>
            <span className="text-sm text-on-surface-variant">
              4 processing • 2 queued
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {ACTIVE_INGESTIONS.map((item) => (
              <GlassCard key={item.name} className="p-5">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-8 h-8 rounded flex items-center justify-center ${item.color}`}
                    >
                      <span className="material-symbols-outlined text-sm">
                        {item.icon}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium truncate w-32">
                        {item.name}
                      </p>
                      <p className="text-[10px] text-on-surface-variant uppercase">
                        {item.stage}
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-primary font-mono">
                    {item.progress}
                  </span>
                </div>
                {item.live ? (
                  <div className="flex gap-0.5 items-end h-1">
                    {[0, 1, 2].map((i) => (
                      <div
                        key={i}
                        className="h-full w-1 bg-secondary animate-pulse"
                      />
                    ))}
                  </div>
                ) : (
                  <div className="h-1 bg-surface-container-highest rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-container"
                      style={{ width: item.progress }}
                    />
                  </div>
                )}
              </GlassCard>
            ))}
          </div>
        </div>

        {/* Recent ingestions table */}
        <div className="lg:col-span-12">
          <GlassCard className="overflow-hidden">
            <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between bg-white/5">
              <h3 className="font-headline-md text-headline-md">
                Recent Ingestions
              </h3>
              <button className="text-primary font-label-md hover:underline flex items-center gap-1">
                Export History
                <span className="material-symbols-outlined text-sm">
                  download
                </span>
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[720px]">
                <thead className="bg-surface-container-low text-on-surface-variant text-[11px] uppercase tracking-widest">
                  <tr>
                    <th className="px-8 py-4 font-medium">Source</th>
                    <th className="px-8 py-4 font-medium">Data Type</th>
                    <th className="px-8 py-4 font-medium">Period</th>
                    <th className="px-8 py-4 font-medium">AI Confidence</th>
                    <th className="px-8 py-4 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {RECENT_ROWS.map((row) => (
                    <tr
                      key={row.source}
                      className="hover:bg-white/[0.02] transition-colors"
                    >
                      <td className="px-8 py-5">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${row.dot}`} />
                          <span className="font-medium">{row.source}</span>
                        </div>
                      </td>
                      <td className="px-8 py-5 text-on-surface-variant">
                        {row.type}
                      </td>
                      <td className="px-8 py-5 text-on-surface-variant">
                        {row.period}
                      </td>
                      <td className="px-8 py-5 font-bold">
                        {row.confidence}
                      </td>
                      <td className="px-8 py-5">
                        <span
                          className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${STATUS_STYLES[row.status]}`}
                        >
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
