import type { Metadata } from "next";
import { GlassCard, Sparkline } from "@/components/ui";

export const metadata: Metadata = {
  title: "Analytics & Reporting Deep Dive",
  description: "High-resolution breakdown of ESG impact vectors.",
};

const SCOPES = [
  {
    tag: "Scope 1",
    icon: "factory",
    title: "Direct Ops",
    description: "On-site combustion and fleet emissions.",
    value: "842.1",
    delta: "4.2%",
    deltaUp: true,
    breakdown: [
      ["Boilers", "342 t"],
      ["Fleet", "500.1 t"],
    ],
  },
  {
    tag: "Scope 2",
    icon: "bolt",
    title: "Indirect Energy",
    description: "Purchased electricity and cooling systems.",
    value: "1,204.5",
    delta: "12.8%",
    deltaUp: false,
    breakdown: [
      ["Grid Mix", "904 t"],
      ["Renewables", "300.5 t"],
    ],
  },
  {
    tag: "Scope 3",
    icon: "lan",
    title: "Value Chain",
    description: "Upstream logistics and employee transit.",
    value: "4,129.0",
    delta: "0.0%",
    deltaUp: null,
    breakdown: [
      ["Suppliers", "3.8k t"],
      ["Transit", "329 t"],
    ],
  },
];

const MATRIX_ROWS = [
  { node: "C-Series Transformer B", id: "#TRANS-902", intensity: "1.22 kg/kWh", delta: "-0.05", status: "STABLE", statusClass: "bg-primary-fixed-dim/10 text-primary-fixed-dim", deltaClass: "text-primary-fixed-dim" },
  { node: "HVAC Loop - Data Center", id: "#COOL-441", intensity: "0.89 kg/kWh", delta: "+0.12", status: "DEVIATION", statusClass: "bg-error/10 text-error", deltaClass: "text-error" },
  { node: "Main Logistics Hub", id: "#LOG-HUB-2", intensity: "4.50 kg/ton", delta: "0.00", status: "NOMINAL", statusClass: "bg-white/5 text-on-surface-variant", deltaClass: "text-on-surface-variant" },
  { node: "Fleet EV Conversion", id: "#AUTO-E1", intensity: "0.04 kg/km", delta: "-0.32", status: "OPTIMIZED", statusClass: "bg-primary-fixed-dim/10 text-primary-fixed-dim", deltaClass: "text-primary-fixed-dim" },
];

export default function AnalyticsPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-12">
      {/* Scopes overview */}
      <section>
        <div className="flex items-end justify-between mb-8">
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface mb-2">
              Emission Scopes
            </h1>
            <p className="text-on-surface-variant font-body-md">
              High-resolution breakdown of ESG impact vectors.
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SCOPES.map((scope) => (
            <GlassCard key={scope.tag} className="p-8 relative overflow-hidden">
              <span className="material-symbols-outlined absolute -right-4 -top-4 text-[120px] opacity-5">
                {scope.icon}
              </span>
              <div className="flex items-center justify-between mb-4">
                <span className="bg-primary-container/20 text-primary-fixed-dim px-3 py-1 rounded-full text-label-sm font-label-sm">
                  {scope.tag}
                </span>
                {scope.deltaUp !== null && (
                  <span
                    className={`flex items-center gap-1 text-label-sm font-bold ${
                      scope.deltaUp ? "text-error" : "text-primary-fixed-dim"
                    }`}
                  >
                    <span className="material-symbols-outlined text-sm">
                      {scope.deltaUp ? "trending_up" : "trending_down"}
                    </span>
                    {scope.delta}
                  </span>
                )}
                {scope.deltaUp === null && (
                  <span className="text-on-surface-variant flex items-center gap-1 text-label-sm font-bold">
                    <span className="material-symbols-outlined text-sm">
                      horizontal_rule
                    </span>
                    {scope.delta}
                  </span>
                )}
              </div>
              <h3 className="font-headline-md text-headline-md text-on-surface mb-1">
                {scope.title}
              </h3>
              <p className="text-on-surface-variant text-body-sm mb-6">
                {scope.description}
              </p>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold font-headline-xl">
                  {scope.value}
                </span>
                <span className="text-on-surface-variant text-label-md">
                  tCO₂e
                </span>
              </div>
              <div className="mt-6 pt-6 border-t border-white/5 grid grid-cols-2 gap-4">
                {scope.breakdown.map(([label, val]) => (
                  <div key={label}>
                    <p className="text-[10px] uppercase tracking-wider text-on-surface-variant mb-1">
                      {label}
                    </p>
                    <p className="text-label-md font-bold">{val}</p>
                  </div>
                ))}
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* Trend explorer */}
      <GlassCard className="overflow-hidden flex flex-col">
        <div className="p-8 flex items-center justify-between border-b border-white/5">
          <div>
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Trend Explorer
            </h2>
            <p className="text-on-surface-variant text-body-sm">
              Cross-system temporal correlation analysis
            </p>
          </div>
          <div className="flex items-center gap-1 bg-surface-container-high p-1 rounded-lg">
            <button className="px-4 py-1.5 rounded text-label-sm font-label-sm text-on-surface-variant">
              Daily
            </button>
            <button className="px-4 py-1.5 rounded text-label-sm font-label-sm bg-primary-fixed-dim text-on-primary">
              Monthly
            </button>
            <button className="px-4 py-1.5 rounded text-label-sm font-label-sm text-on-surface-variant">
              Yearly
            </button>
          </div>
        </div>
        <div className="relative h-[320px] w-full p-8">
          <Sparkline
            path="M0,280 L100,260 L200,290 L300,180 L400,210 L500,140 L600,160 L700,90 L800,110 L900,60 L1000,80"
            viewBox="0 0 1000 400"
            color="#00e38b"
            height="100%"
          />
        </div>
        <div className="p-8 bg-black/10 border-t border-white/5 flex flex-wrap gap-8">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-primary-fixed-dim" />
            <div>
              <p className="text-label-sm font-label-sm text-on-surface">
                Indirect Energy (S2)
              </p>
              <p className="text-[10px] text-on-surface-variant">
                Real-time kWh conversion
              </p>
            </div>
          </div>
          <div className="ml-auto flex items-center gap-4">
            <div className="text-right">
              <p className="text-[10px] text-on-surface-variant uppercase tracking-widest">
                Confidence Score
              </p>
              <p className="text-label-md font-bold text-primary-fixed-dim">
                98.4%
              </p>
            </div>
            <span className="material-symbols-outlined text-primary-fixed-dim w-10 h-10 rounded-full border-2 border-primary-fixed-dim flex items-center justify-center">
              shield_lock
            </span>
          </div>
        </div>
      </GlassCard>

      {/* Comparison module */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-6">
          <GlassCard className="p-8">
            <h3 className="font-headline-md text-headline-md text-on-surface mb-6">
              Historical Baseline
            </h3>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-on-surface-variant text-label-md">
                  2023 Average
                </span>
                <span className="font-bold">2.4k tCO₂e</span>
              </div>
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div className="bg-primary-fixed-dim h-full w-3/4 rounded-full" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-on-surface-variant text-label-md">
                  Current Deviation
                </span>
                <span className="text-primary-fixed-dim font-bold">
                  -14.2%
                </span>
              </div>
            </div>
            <button className="w-full mt-8 border border-white/10 hover:border-primary-fixed-dim transition-colors py-3 rounded-lg text-label-sm font-label-sm">
              Download Report
            </button>
          </GlassCard>
          <div className="bg-surface-container-highest p-8 rounded-xl border border-white/5 relative overflow-hidden">
            <span className="material-symbols-outlined absolute -bottom-4 -right-4 text-[80px] text-white opacity-5">
              award_star
            </span>
            <h3 className="text-label-md font-bold text-tertiary-fixed-dim mb-2 uppercase tracking-widest">
              Industry Benchmark
            </h3>
            <p className="text-headline-md font-headline-md text-on-surface mb-4">
              Top 5% Performer
            </p>
            <p className="text-on-surface-variant text-body-sm leading-relaxed">
              Your current efficiency rating is 18 points above the
              ISO-14064 sector average.
            </p>
          </div>
        </div>

        <div className="lg:col-span-8">
          <GlassCard className="overflow-hidden">
            <div className="p-8 border-b border-white/5">
              <h3 className="font-headline-md text-headline-md text-on-surface">
                Data Precision Matrix
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[640px]">
                <thead className="bg-black/20">
                  <tr>
                    <th className="px-8 py-4 text-[10px] uppercase tracking-widest text-on-surface-variant">
                      Protocol Node
                    </th>
                    <th className="px-8 py-4 text-[10px] uppercase tracking-widest text-on-surface-variant">
                      Intensity
                    </th>
                    <th className="px-8 py-4 text-[10px] uppercase tracking-widest text-on-surface-variant">
                      Delta
                    </th>
                    <th className="px-8 py-4 text-[10px] uppercase tracking-widest text-on-surface-variant">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {MATRIX_ROWS.map((row) => (
                    <tr
                      key={row.id}
                      className="hover:bg-white/5 transition-colors"
                    >
                      <td className="px-8 py-5">
                        <p className="text-label-md font-bold text-on-surface">
                          {row.node}
                        </p>
                        <p className="text-[10px] text-on-surface-variant">
                          Node ID: {row.id}
                        </p>
                      </td>
                      <td className="px-8 py-5 font-bold">
                        {row.intensity}
                      </td>
                      <td className={`px-8 py-5 font-bold ${row.deltaClass}`}>
                        {row.delta}
                      </td>
                      <td className="px-8 py-5">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.statusClass}`}
                        >
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="p-4 bg-black/10 text-center">
              <button className="text-label-sm font-label-sm text-primary-fixed-dim hover:underline transition-all">
                View All 152 Nodes
              </button>
            </div>
          </GlassCard>
        </div>
      </section>
    </div>
  );
}
