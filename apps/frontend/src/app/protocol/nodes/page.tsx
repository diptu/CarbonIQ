import type { Metadata } from "next";
import { GlassCard, Sparkline } from "@/components/ui";
import { ProtocolSidebar } from "@/components/protocol/ProtocolSidebar";

export const metadata: Metadata = {
  title: "Node Status",
  description: "Real-time telemetry from the global CarbonIQ decentralized cluster.",
};

const KPIS = [
  { icon: "hub", label: "Active Nodes", value: "124", note: "+4 since yesterday", noteIcon: "trending_up" },
  { icon: "timer", label: "Network Uptime", value: "99.98%", note: "Last outage: 42 days ago" },
  { icon: "speed", label: "Avg Block Time", value: "1.2", unit: "s", note: "Highly optimized", noteIcon: "bolt" },
  { icon: "token", label: "Staked Credits", value: "4.8M", unit: "CRB", note: "Total value locked" },
];

const NODES = [
  { id: "CIQ-US-8821", region: "Oregon, US", provider: "AWS-1", status: "Active", version: "v2.4.0-stable", score: "98" },
  { id: "CIQ-DE-0192", region: "Frankfurt, DE", provider: "HETZ-4", status: "Syncing", version: "v2.4.0-stable", score: "--" },
  { id: "CIQ-JP-4431", region: "Tokyo, JP", provider: "GCP-C", status: "Active", version: "v2.3.9-patch", score: "94" },
  { id: "CIQ-FR-9102", region: "Paris, FR", provider: "LOCAL-1", status: "Offline", version: "v2.4.0-stable", score: "0" },
];

const STATUS_STYLES: Record<string, string> = {
  Active: "bg-primary-container text-primary-container",
  Syncing: "bg-secondary-fixed-dim text-secondary-fixed-dim animate-pulse",
  Offline: "bg-error text-error",
};

export default function NodeStatusPage() {
  return (
    <div className="min-h-screen">
      <ProtocolSidebar />
      <main className="lg:ml-64 p-6 md:p-margin-desktop min-h-screen">
        <header className="flex flex-col md:flex-row justify-between md:items-end gap-6 mb-10">
          <div>
            <nav className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm mb-2">
              <span>Protocols</span>
              <span className="material-symbols-outlined text-[14px]">
                chevron_right
              </span>
              <span className="text-primary-fixed-dim">Node Status</span>
            </nav>
            <h1 className="font-headline-xl text-headline-xl tracking-tighter">
              Validator Health
            </h1>
            <p className="text-on-surface-variant font-body-md text-body-md mt-2">
              Real-time telemetry from the global CarbonIQ decentralized
              cluster.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-surface-container-high border border-outline-variant/30 rounded-full flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
              <span className="font-label-sm text-label-sm text-primary-fixed-dim uppercase tracking-widest">
                Network Live
              </span>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-gutter mb-10">
          {KPIS.map((kpi) => (
            <GlassCard key={kpi.label} className="p-6 relative overflow-hidden">
              <span className="material-symbols-outlined absolute top-0 right-0 p-4 text-[48px] opacity-10">
                {kpi.icon}
              </span>
              <p className="text-on-surface-variant font-label-md text-label-md mb-2">
                {kpi.label}
              </p>
              <h3 className="text-headline-lg font-headline-lg text-primary-fixed-dim">
                {kpi.value}
                {kpi.unit && (
                  <span className="text-headline-md ml-1">{kpi.unit}</span>
                )}
              </h3>
              <div className="mt-4 flex items-center gap-1 text-[12px] text-on-surface-variant">
                {kpi.noteIcon && (
                  <span className="material-symbols-outlined text-[16px] text-primary-container">
                    {kpi.noteIcon}
                  </span>
                )}
                <span>{kpi.note}</span>
              </div>
            </GlassCard>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter mb-10">
          <GlassCard className="lg:col-span-8 overflow-hidden h-[360px] relative flex items-center justify-center bg-gradient-to-br from-primary-container/5 to-surface-container">
            <div className="absolute top-6 left-6 z-10">
              <div className="bg-background/80 backdrop-blur px-3 py-1.5 rounded-lg border border-outline-variant/30 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-primary-container" />
                <span className="font-label-sm text-label-sm">
                  Global Distribution
                </span>
              </div>
            </div>
            <span className="material-symbols-outlined text-[180px] text-primary-container/10">
              public
            </span>
            <div className="absolute bottom-6 right-6 flex items-center gap-4 bg-surface-container-lowest/80 backdrop-blur p-4 rounded-xl border border-outline-variant/30">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary-container" />
                <span className="text-[11px] text-on-surface font-label-md">
                  High Density
                </span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="lg:col-span-4 p-6 flex flex-col">
            <div className="flex justify-between items-start mb-6">
              <h4 className="font-label-md text-label-md text-primary-fixed-dim uppercase tracking-widest">
                Network Latency
              </h4>
              <span className="text-[12px] text-on-surface-variant">
                Last 24h
              </span>
            </div>
            <div className="flex-1 flex flex-col justify-end">
              <div className="h-48">
                <Sparkline
                  path="M0,120 Q50,110 100,130 T200,90 T300,110 T400,100"
                  viewBox="0 0 400 150"
                  color="#00e38b"
                  height="100%"
                />
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2">
                <div className="text-center">
                  <p className="text-[10px] text-on-surface-variant uppercase">
                    Min
                  </p>
                  <p className="text-body-md font-semibold">12ms</p>
                </div>
                <div className="text-center border-x border-outline-variant/30">
                  <p className="text-[10px] text-on-surface-variant uppercase">
                    Avg
                  </p>
                  <p className="text-body-md font-semibold text-primary-fixed-dim">
                    48ms
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] text-on-surface-variant uppercase">
                    Max
                  </p>
                  <p className="text-body-md font-semibold">112ms</p>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>

        <GlassCard className="overflow-hidden mb-10">
          <div className="px-8 py-6 flex justify-between items-center border-b border-outline-variant/20">
            <h3 className="font-headline-md text-headline-md">
              Node Directory
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[720px]">
              <thead className="bg-surface-container-low">
                <tr>
                  <th className="px-8 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-widest">
                    Node ID
                  </th>
                  <th className="px-8 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-widest">
                    Region
                  </th>
                  <th className="px-8 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-widest">
                    Status
                  </th>
                  <th className="px-8 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-widest">
                    Version
                  </th>
                  <th className="px-8 py-4 font-label-md text-label-md text-on-surface-variant uppercase tracking-widest text-right">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/10">
                {NODES.map((node) => (
                  <tr
                    key={node.id}
                    className={`hover:bg-surface-container-high/30 transition-colors ${
                      node.status === "Offline" ? "opacity-70" : ""
                    }`}
                  >
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-primary-container/10 flex items-center justify-center border border-primary-container/20">
                          <span className="material-symbols-outlined text-[16px] text-primary-fixed-dim">
                            dns
                          </span>
                        </div>
                        <span className="font-mono text-body-md">
                          {node.id}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-2">
                        <span className="text-body-md">{node.region}</span>
                        <span className="text-[10px] px-2 py-0.5 bg-surface-container-high border border-outline-variant/40 rounded text-on-surface-variant uppercase font-label-sm">
                          {node.provider}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-2">
                        <span
                          className={`w-2 h-2 rounded-full ${STATUS_STYLES[node.status].split(" ")[0]}`}
                        />
                        <span
                          className={`text-body-md font-medium ${STATUS_STYLES[node.status].split(" ")[1]}`}
                        >
                          {node.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-5 text-on-surface-variant font-body-sm">
                      {node.version}
                    </td>
                    <td className="px-8 py-5 text-right">
                      <div className="inline-flex items-center gap-2 bg-primary-container/5 px-3 py-1 rounded-full border border-primary-container/10">
                        <span className="text-headline-md font-bold text-primary-fixed-dim">
                          {node.score}
                        </span>
                        <span className="text-[10px] text-on-surface-variant uppercase">
                          score
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-8 py-4 bg-surface-container-low flex justify-between items-center">
            <span className="text-body-sm text-on-surface-variant">
              Showing 4 of 124 validators
            </span>
          </div>
        </GlassCard>
      </main>
    </div>
  );
}
