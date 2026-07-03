import type { Metadata } from "next";
import { GlassCard, Sparkline, MetricCircle } from "@/components/ui";

export const metadata: Metadata = {
  title: "Lens View",
  description: "Real-time carbon equivalent tracking across the ecosystem.",
};

const ALERTS = [
  "[14:22] Methane spike detected in Sector 4 Substation. Protocol EPS-9 engaged.",
  "[13:58] Grid Efficiency drop in Northern Cluster (2.4%). Cooling systems under maintenance.",
  "[13:12] Annual Sustainability Audit scheduled for Facility-7. Data prep 85% complete.",
  "[12:45] New regulatory threshold V2.4 applied to all microservices.",
];

const SPARK_CARDS = [
  {
    label: "Solar Capture",
    value: "1,240 kW/h",
    delta: "+12.5%",
    positive: true,
    path: "M0 35 Q10 32 20 38 T40 30 T60 35 T80 25 T100 28",
  },
  {
    label: "Water Recirc",
    value: "94.2%",
    delta: "+0.8%",
    positive: true,
    path: "M0 20 Q15 15 30 25 T60 10 T90 15 T100 5",
  },
  {
    label: "Grid Leakage",
    value: "12 ppm",
    delta: "+3.1%",
    positive: false,
    path: "M0 38 Q20 30 40 32 T70 38 T100 20",
  },
];

export default function DashboardLensPage() {
  return (
    <div className="p-8 md:p-12 max-w-7xl mx-auto space-y-8">
      {/* Alert ticker */}
      <div className="w-full bg-surface-container-low border border-error-container/20 rounded-lg overflow-hidden py-3 flex items-center">
        <div className="px-4 border-r border-error/30 text-error font-bold font-label-sm uppercase flex items-center gap-2 shrink-0">
          <span className="material-symbols-outlined text-[16px]">
            emergency
          </span>
          High Priority
        </div>
        <div className="px-4 text-on-surface-variant font-label-md italic truncate">
          {ALERTS.join("     ")}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-gutter">
        {/* Live emissions tally */}
        <GlassCard className="col-span-12 lg:col-span-8 p-8 flex flex-col justify-between min-h-[320px]">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
                Live Emissions Tally
              </h2>
              <p className="text-on-surface-variant font-label-md mt-1">
                Real-time Carbon Equivalent (CO2e) tracking
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-primary-container/10 border border-primary-container/20 rounded-full">
              <span className="w-2 h-2 bg-primary-fixed-dim rounded-full animate-pulse" />
              <span className="text-primary-fixed-dim font-label-sm uppercase">
                Live Stream
              </span>
            </div>
          </div>
          <div className="flex items-baseline gap-4 mt-8">
            <span className="font-headline-xl text-[64px] leading-none text-primary-fixed-dim font-bold">
              42,891.02
            </span>
            <span className="text-headline-md text-on-surface-variant mb-2">
              Metric Tons / Hour
            </span>
          </div>
          <div className="grid grid-cols-3 gap-6 mt-12 border-t border-white/5 pt-8">
            <div>
              <p className="text-on-surface-variant font-label-sm uppercase tracking-widest mb-2">
                Trend (24h)
              </p>
              <div className="flex items-center gap-2 text-primary-fixed-dim">
                <span className="material-symbols-outlined">
                  trending_down
                </span>
                <span className="font-bold">-4.2%</span>
              </div>
            </div>
            <div>
              <p className="text-on-surface-variant font-label-sm uppercase tracking-widest mb-2">
                Peak Rate
              </p>
              <div className="font-bold text-on-surface">45,102.40 MT</div>
            </div>
            <div>
              <p className="text-on-surface-variant font-label-sm uppercase tracking-widest mb-2">
                System Load
              </p>
              <div className="font-bold text-on-surface">92% Optimal</div>
            </div>
          </div>
        </GlassCard>

        {/* Eco-health gauge */}
        <GlassCard className="col-span-12 lg:col-span-4 p-8 flex flex-col items-center text-center">
          <div className="w-full flex justify-between mb-8">
            <span className="font-label-md text-label-md text-on-surface-variant font-bold uppercase tracking-widest">
              Eco-Health Score
            </span>
            <span className="material-symbols-outlined text-on-surface-variant">
              info
            </span>
          </div>
          <MetricCircle percent={88} size={192} />
          <p className="mt-8 text-on-surface-variant font-body-sm px-4">
            Proprietary metric based on emissions, energy offset, and
            resource recycling efficiency.
          </p>
        </GlassCard>

        {/* Sparkline row */}
        <div className="col-span-12 grid grid-cols-1 md:grid-cols-3 gap-gutter">
          {SPARK_CARDS.map((card) => (
            <GlassCard key={card.label} className="p-8 flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <div className="flex flex-col">
                  <span className="font-label-sm text-on-surface-variant uppercase tracking-widest">
                    {card.label}
                  </span>
                  <span className="font-headline-md text-headline-md text-on-surface">
                    {card.value}
                  </span>
                </div>
                <span
                  className={`px-2 py-0.5 rounded font-bold text-xs ${
                    card.positive
                      ? "text-primary-fixed-dim bg-primary-container/10"
                      : "text-error bg-error-container/10"
                  }`}
                >
                  {card.delta}
                </span>
              </div>
              <div className="h-16">
                <Sparkline
                  path={card.path}
                  color={card.positive ? "#00e38b" : "#ffb4ab"}
                />
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Facility overview */}
        <GlassCard className="col-span-12 grid grid-cols-1 lg:grid-cols-2 gap-12 p-8">
          <div className="flex flex-col justify-center">
            <span className="font-label-md text-primary-fixed-dim font-bold mb-2 uppercase tracking-widest">
              Active Facility
            </span>
            <h3 className="font-headline-lg text-headline-lg text-on-surface mb-4">
              Neo-Lagos Industrial Cluster Alpha
            </h3>
            <p className="text-on-surface-variant mb-8 font-body-md leading-relaxed">
              A primary ESG focal point for this year. This facility
              currently contributes 14% of the global efficiency gains.
              Recent integration of Carbon Capture Array 4 has reduced
              operational footprint by 2,200 tons monthly.
            </p>
            <div className="flex gap-4">
              <div className="bg-black/20 p-4 rounded-xl border border-white/5 flex flex-col">
                <span className="font-label-sm text-on-surface-variant">
                  Sensors Active
                </span>
                <span className="font-headline-md text-on-surface">1,842</span>
              </div>
              <div className="bg-black/20 p-4 rounded-xl border border-white/5 flex flex-col">
                <span className="font-label-sm text-on-surface-variant">
                  Health Status
                </span>
                <span className="font-headline-md text-primary-fixed-dim">
                  OPTIMAL
                </span>
              </div>
            </div>
          </div>
          <div className="relative rounded-xl overflow-hidden min-h-[240px] border border-white/10 bg-gradient-to-br from-primary-container/10 to-surface-container flex items-center justify-center">
            <span className="material-symbols-outlined text-[96px] text-primary-container/20">
              factory
            </span>
            <button className="absolute bottom-6 left-6 bg-white/10 backdrop-blur-md px-4 py-2 rounded-lg border border-white/20 text-white font-label-md hover:bg-white/20 transition-all flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">
                videocam
              </span>
              Live Feed View
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
