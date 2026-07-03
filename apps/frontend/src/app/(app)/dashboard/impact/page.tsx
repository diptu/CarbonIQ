import type { Metadata } from "next";
import { GlassCard, Sparkline } from "@/components/ui";

export const metadata: Metadata = {
  title: "Granular Impact Dashboard",
  description: "Global ESG performance index and carbon intensity tracking.",
};

export default function DashboardImpactPage() {
  return (
    <div className="p-8 md:p-12 max-w-7xl mx-auto grid grid-cols-12 gap-gutter">
      {/* Impact score gauge */}
      <GlassCard className="col-span-12 lg:col-span-4 p-8 flex flex-col items-center justify-center text-center">
        <div className="mb-6">
          <h2 className="font-label-md text-label-md uppercase tracking-widest text-primary-fixed">
            Impact Score
          </h2>
          <p className="text-on-surface-variant text-xs mt-1">
            Global ESG Performance Index
          </p>
        </div>
        <div className="relative w-48 h-48 flex items-center justify-center">
          <svg className="w-full h-full -rotate-90">
            <circle
              className="text-white/5"
              cx="96"
              cy="96"
              fill="transparent"
              r="88"
              stroke="currentColor"
              strokeWidth="8"
            />
            <circle
              className="text-primary-fixed neon-glow"
              cx="96"
              cy="96"
              fill="transparent"
              r="88"
              stroke="currentColor"
              strokeDasharray="552.92"
              strokeDashoffset="110.58"
              strokeLinecap="round"
              strokeWidth="12"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-headline-xl text-headline-xl text-white">
              82
            </span>
            <span className="font-label-md text-label-md text-primary-fixed font-bold">
              OPTIMIZED
            </span>
          </div>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-8 w-full">
          <div className="text-center">
            <p className="text-xs text-on-surface-variant uppercase mb-1">
              Status
            </p>
            <div className="flex items-center justify-center gap-1">
              <span className="w-2 h-2 rounded-full bg-primary-fixed animate-pulse" />
              <span className="font-bold text-sm text-primary">Live</span>
            </div>
          </div>
          <div className="text-center">
            <p className="text-xs text-on-surface-variant uppercase mb-1">
              Trust
            </p>
            <div className="flex items-center justify-center gap-1">
              <span className="material-symbols-outlined text-primary-fixed text-sm">
                verified
              </span>
              <span className="font-bold text-sm text-primary">Verified</span>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Carbon intensity sparkline */}
      <GlassCard className="col-span-12 lg:col-span-8 p-8 flex flex-col">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="font-headline-md text-headline-md text-white mb-1">
              Carbon Intensity
            </h2>
            <p className="text-on-surface-variant text-body-sm font-body-sm">
              gCO₂e per kWh • System-wide Aggregation
            </p>
          </div>
          <div className="text-right">
            <p className="text-headline-md font-headline-md text-primary-fixed">
              142.4
            </p>
            <p className="text-xs text-error flex items-center justify-end gap-1">
              <span className="material-symbols-outlined text-xs">
                trending_up
              </span>{" "}
              +2.4% vs last hour
            </p>
          </div>
        </div>
        <div className="flex-1 w-full min-h-[160px] mt-4">
          <Sparkline
            path="M0 140 Q 50 130, 100 150 T 200 120 T 300 140 T 400 100 T 500 130 T 600 110 T 700 140 T 800 80"
            viewBox="0 0 800 160"
            color="#00FF9D"
            height={160}
          />
        </div>
      </GlassCard>
    </div>
  );
}
