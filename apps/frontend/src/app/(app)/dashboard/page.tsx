import type { Metadata } from "next";
import { GlassCard, StatusBadge } from "@/components/ui";

export const metadata: Metadata = {
  title: "Protocol Overview",
  description: "Real-time telemetry of the decentralized carbon market.",
};

const HERO_METRICS = [
  {
    label: "Total CO2e Offset",
    value: "1.2M",
    unit: "Tons",
    icon: "eco",
  },
  {
    label: "Active Projects",
    value: "42",
    unit: "Global",
    trend: "+8.2% from last epoch",
    icon: "public",
  },
  {
    label: "Verified Yield",
    value: "89.4",
    unit: "%",
    icon: "check_circle",
  },
];

const VERIFICATIONS = [
  {
    icon: "forest",
    name: "Amazon Rainbelt #092",
    phase: "Protocol Phase: Bio-Acoustic Monitoring",
    progress: 78,
    status: "IN PROGRESS" as const,
  },
  {
    icon: "water_drop",
    name: "Ocean Kelp Farm v2",
    phase: "Protocol Phase: Blue Carbon Tallying",
    progress: 42,
    status: "QUEUED" as const,
  },
  {
    icon: "landscape",
    name: "Andean Highland Reforest",
    phase: "Protocol Phase: Final Certification",
    progress: 95,
    status: "VERIFYING" as const,
  },
];

const CREDITS = [
  { id: "T-CORE #8812", project: "CONGO BASIN RESTORATION", tons: "1,400", age: "2 mins ago" },
  { id: "T-CORE #8811", project: "SAHARA GREEN WALL", tons: "3,250", age: "14 mins ago" },
  { id: "T-CORE #8810", project: "ARCTIC PEATLAND PROTECTION", tons: "820", age: "1 hour ago" },
  { id: "T-CORE #8809", project: "ALGAE BIO-REACTOR UNIT 4", tons: "4,120", age: "3 hours ago" },
];

export default function DashboardPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto">
      <section className="mb-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
          <div>
            <h2 className="font-headline-xl text-headline-xl text-primary">
              Protocol Overview
            </h2>
            <p className="text-on-surface-variant mt-2 font-body-lg text-body-lg">
              Real-time telemetry of the decentralized carbon market.
            </p>
          </div>
          <div className="bg-surface-container px-4 py-2 rounded-lg border border-white/5">
            <p className="text-[10px] text-on-surface-variant/60 font-bold uppercase tracking-widest">
              Network Status
            </p>
            <p className="text-primary-container font-label-md text-label-md">
              Optimized: 14.2 TPS
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          {HERO_METRICS.map((metric) => (
            <GlassCard
              key={metric.label}
              className="p-8 flex flex-col justify-between h-48 relative overflow-hidden"
            >
              <div className="relative z-10">
                <p className="text-on-surface-variant font-label-md text-label-md mb-2">
                  {metric.label}
                </p>
                <h3 className="font-headline-xl text-headline-xl text-primary">
                  {metric.value}{" "}
                  <span className="text-body-lg opacity-60">
                    {metric.unit}
                  </span>
                </h3>
              </div>
              {metric.trend && (
                <div className="flex items-center gap-2 text-primary-container text-label-md mt-4">
                  <span className="material-symbols-outlined text-sm">
                    trending_up
                  </span>
                  <span>{metric.trend}</span>
                </div>
              )}
              <span className="material-symbols-outlined absolute -right-4 -bottom-4 text-[120px] opacity-5">
                {metric.icon}
              </span>
            </GlassCard>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        <section className="lg:col-span-8">
          <GlassCard className="p-8 h-full">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h4 className="font-headline-md text-headline-md text-primary">
                  Active Verifications
                </h4>
                <p className="text-on-surface-variant font-body-sm text-body-sm mt-1">
                  Satellite audit progress of ecosystem protocols.
                </p>
              </div>
              <button className="text-primary-container font-label-md text-label-md flex items-center gap-1 hover:underline">
                View History{" "}
                <span className="material-symbols-outlined text-[16px]">
                  arrow_forward
                </span>
              </button>
            </div>
            <div className="space-y-6">
              {VERIFICATIONS.map((item) => (
                <div
                  key={item.name}
                  className="bg-surface-container-high/40 p-4 rounded-lg flex items-center justify-between hover:bg-surface-container-high/60 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded bg-surface flex items-center justify-center text-primary-container border border-white/5">
                      <span className="material-symbols-outlined">
                        {item.icon}
                      </span>
                    </div>
                    <div>
                      <p className="font-label-md text-label-md text-on-surface">
                        {item.name}
                      </p>
                      <p className="text-[12px] text-on-surface-variant">
                        {item.phase}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right hidden md:block">
                      <div className="w-32 h-1.5 bg-surface rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-container"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-primary-container mt-1 font-bold">
                        {item.progress}% COMPLETE
                      </p>
                    </div>
                    <div className="px-3 py-1 rounded-full bg-primary-container/10 border border-primary-container/30 text-primary-container text-[11px] font-bold">
                      {item.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </section>

        <aside className="lg:col-span-4">
          <GlassCard className="h-full flex flex-col overflow-hidden">
            <div className="p-6 border-b border-white/10">
              <h4 className="font-headline-md text-headline-md text-primary">
                Global Impact
              </h4>
              <p className="text-on-surface-variant font-body-sm text-body-sm">
                Active project distribution.
              </p>
            </div>
            <div className="flex-1 relative min-h-[240px] flex items-center justify-center">
              <span className="material-symbols-outlined text-[140px] text-primary-container/10">
                public
              </span>
              <div className="absolute top-1/3 left-1/3 p-2 bg-surface-container-highest border border-primary-container rounded shadow-2xl flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary-container" />
                <span className="text-[10px] font-bold">AMAZON-092: LIVE</span>
              </div>
            </div>
            <div className="p-6 bg-surface-container/40">
              <div className="flex items-center justify-between text-label-sm font-label-sm text-on-surface-variant">
                <span>Most active region</span>
                <span className="text-primary">Sub-Saharan Africa</span>
              </div>
            </div>
          </GlassCard>
        </aside>
      </div>

      <section className="mt-12">
        <div className="mb-8">
          <h4 className="font-headline-md text-headline-md text-primary">
            Latest Minted Credits
          </h4>
          <p className="text-on-surface-variant font-body-sm text-body-sm mt-1">
            Recent batch issuance on the Verified Ledger.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-gutter">
          {CREDITS.map((credit) => (
            <GlassCard
              key={credit.id}
              className="overflow-hidden flex flex-col transition-all hover:-translate-y-2"
            >
              <div className="aspect-video relative overflow-hidden bg-gradient-to-br from-primary-container/20 to-surface-container flex items-center justify-center">
                <span className="material-symbols-outlined text-[64px] text-primary-container/30">
                  forest
                </span>
                <div className="absolute top-3 right-3">
                  <StatusBadge variant="verified">Verified</StatusBadge>
                </div>
              </div>
              <div className="p-5 flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h5 className="text-primary font-label-md text-label-md">
                      {credit.id}
                    </h5>
                    <p className="text-[11px] text-on-surface-variant font-medium">
                      {credit.project}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-secondary font-label-md text-label-md">
                      {credit.tons}
                    </p>
                    <p className="text-[10px] text-on-surface-variant uppercase">
                      TONS
                    </p>
                  </div>
                </div>
                <div className="mt-auto pt-4 border-t border-white/5 flex items-center justify-between">
                  <p className="text-[10px] text-on-surface-variant/60 font-mono">
                    {credit.age}
                  </p>
                  <span className="material-symbols-outlined text-[20px] text-on-surface hover:text-primary-container transition-colors cursor-pointer">
                    open_in_new
                  </span>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </section>
    </div>
  );
}
