import type { Metadata } from "next";
import { GlassCard, Sparkline } from "@/components/ui";

export const metadata: Metadata = {
  title: "AI Estimation & Load Profiling",
  description: "Reconstructing high-fidelity energy profiles with temporal fusion transformers.",
};

const GAPS = [
  {
    id: "#GAP-2023-08-12",
    title: "Missing Aug 2023 Interval",
    detail: "24h telemetry outage from main meter.",
    status: "Pending",
    impact: "~1.2 MWh",
  },
  {
    id: "#ANM-2023-08-14",
    title: "Anomalous Consumption Spike",
    detail: "300% deviation from historical baseline (HVAC fault).",
    status: "Smoothing Recom.",
    impact: "~4.5 MWh",
  },
  {
    id: "#GAP-2023-08-28",
    title: "Partial Segment Dropout",
    detail: "Intermittent signal loss over 4 hour period.",
    status: "Pending",
    impact: "~0.4 MWh",
  },
];

const STATUS_STYLES: Record<string, string> = {
  Pending: "bg-error/10 text-error border-error/20",
  "Smoothing Recom.": "bg-secondary-container/20 text-secondary-fixed border-secondary-fixed/30",
};

export default function AiEstimationPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto pb-32">
      <header className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <nav className="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm mb-2">
            <span>Projects</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span>Tesla Giga Berlin</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-primary">Load Profiling</span>
          </nav>
          <h1 className="font-headline-xl text-headline-xl text-primary tracking-tight">
            AI Estimation &amp; Load Profiling
          </h1>
          <p className="text-on-surface-variant mt-2 max-w-2xl">
            Reconstructing high-fidelity energy profiles through temporal
            fusion transformers and pattern-matching heuristics.
          </p>
        </div>
        <button className="flex items-center gap-2 bg-primary-container text-on-primary-container px-6 py-3 rounded-xl font-label-md text-label-md font-bold hover:scale-[1.02] active:scale-95 transition-all neon-glow">
          <span className="material-symbols-outlined">verified</span>
          Commit Estimations to Ledger
        </button>
      </header>

      <div className="grid grid-cols-12 gap-gutter">
        {/* Gap analysis hero */}
        <GlassCard className="col-span-12 p-8 relative overflow-hidden">
          <span className="material-symbols-outlined absolute top-0 right-0 p-8 text-[120px] text-primary-container opacity-20">
            query_stats
          </span>
          <h2 className="font-headline-md text-headline-md text-on-surface mb-6 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container">
              analytics
            </span>
            Gap Analysis Dashboard
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2 flex flex-col justify-center">
              <div className="flex justify-between items-end mb-4">
                <span className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
                  Completeness Lift
                </span>
                <span className="text-primary-container font-headline-md text-headline-md">
                  +21.8%
                </span>
              </div>
              <div className="h-12 w-full bg-white/5 rounded-full p-1.5 flex overflow-hidden border border-white/10">
                <div className="h-full bg-white/10 rounded-full flex items-center justify-center px-4 w-[78%]">
                  <span className="text-[10px] font-bold text-on-surface-variant">
                    78% RAW
                  </span>
                </div>
                <div className="h-full bg-primary-container rounded-full shadow-[0_0_15px_rgba(0,255,157,0.4)] flex items-center justify-center px-4 w-[22%]">
                  <span className="text-[10px] font-bold text-on-primary-container whitespace-nowrap">
                    99.8% AI ENHANCED
                  </span>
                </div>
              </div>
            </div>
            <div className="bg-white/5 rounded-2xl p-6 border border-white/10 flex flex-col items-center justify-center text-center">
              <span className="font-label-md text-label-md text-on-surface-variant mb-2">
                Inference Accuracy
              </span>
              <span className="text-[48px] font-black text-primary leading-none mb-2">
                96.2%
              </span>
              <div className="flex items-center gap-1 text-[12px] font-bold text-primary-container bg-primary-container/10 px-2 py-1 rounded-full">
                <span className="material-symbols-outlined text-[14px]">
                  shield_lock
                </span>
                High Confidence
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Load profile reconstruction */}
        <GlassCard className="col-span-12 lg:col-span-8 p-8 h-[440px] flex flex-col">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface">
                Load Profile Reconstruction
              </h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Facility: Tesla Giga Berlin • Period: Aug 2023
              </p>
            </div>
            <div className="flex items-center gap-1 bg-white/5 p-1 rounded-lg border border-white/10">
              <button className="px-4 py-1.5 rounded-md text-label-sm font-bold bg-primary-container text-on-primary-container">
                Day
              </button>
              <button className="px-4 py-1.5 rounded-md text-label-sm font-bold text-on-surface-variant hover:text-on-surface">
                Week
              </button>
              <button className="px-4 py-1.5 rounded-md text-label-sm font-bold text-on-surface-variant hover:text-on-surface">
                Month
              </button>
            </div>
          </div>
          <div className="flex-1 relative border-l border-b border-white/10">
            <Sparkline
              path="M0,80 Q10,75 20,85 T40,60 T60,70 T80,30 T100,50"
              viewBox="0 0 100 100"
              color="#00ff9d"
            />
            <div className="absolute top-0 left-[25%] w-[12%] h-full bg-error/5 border-x border-error/20" />
            <div className="absolute top-0 left-[70%] w-[10%] h-full bg-error/5 border-x border-error/20" />
          </div>
          <div className="mt-6 flex items-center gap-8">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-primary-container" />
              <span className="text-label-sm text-on-surface">
                AI Inferred Profile
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-white/20 border border-white/30 rounded-sm" />
              <span className="text-label-sm text-on-surface-variant">
                Fragmented Raw Data
              </span>
            </div>
          </div>
        </GlassCard>

        {/* AI insights panel */}
        <GlassCard className="col-span-12 lg:col-span-4 p-8 flex flex-col">
          <h3 className="font-headline-md text-headline-md text-primary mb-6">
            AI Insights Panel
          </h3>
          <div className="space-y-6 flex-1">
            <div className="bg-white/5 rounded-2xl p-5 border border-white/10">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-secondary-fixed">
                    neurology
                  </span>
                  <span className="font-label-md text-label-md text-on-surface">
                    Primary Model
                  </span>
                </div>
                <span className="text-[10px] font-bold text-secondary-fixed border border-secondary-fixed/30 px-2 py-0.5 rounded uppercase">
                  Active
                </span>
              </div>
              <p className="font-headline-md text-headline-md text-white mb-1">
                Temporal Fusion Transformer
              </p>
              <p className="text-on-surface-variant text-body-sm leading-relaxed">
                Multi-horizon prediction utilizing gated residual networks
                to learn complex temporal patterns.
              </p>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-label-sm text-on-surface-variant">
                  Model Confidence
                </span>
                <span className="text-label-sm font-black text-secondary-fixed">
                  98.4%
                </span>
              </div>
            </div>
            <div className="bg-white/5 rounded-2xl p-5 border border-white/10">
              <div className="flex items-center gap-2 mb-3">
                <span className="material-symbols-outlined text-tertiary-fixed">
                  hub
                </span>
                <span className="font-label-md text-label-md text-on-surface">
                  Secondary Heuristic
                </span>
              </div>
              <p className="font-headline-md text-headline-md text-white mb-1">
                LSTM-based Pattern Match
              </p>
              <p className="text-on-surface-variant text-body-sm leading-relaxed">
                Long Short-Term Memory networks identifying repeating
                daily/weekly consumption signatures.
              </p>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-label-sm text-on-surface-variant">
                  Match Reliability
                </span>
                <span className="text-label-sm font-black text-tertiary-fixed">
                  92.1%
                </span>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/10">
            <div className="bg-primary/5 rounded-2xl p-4 flex gap-4">
              <span className="material-symbols-outlined text-primary-container w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                lightbulb
              </span>
              <div>
                <p className="text-label-md font-bold text-primary mb-1">
                  Optimization Suggestion
                </p>
                <p className="text-body-sm text-on-surface-variant">
                  Switching to 15-min interval granularity could increase
                  accuracy by 1.2% for the Berlin facility.
                </p>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Estimation workspace table */}
        <GlassCard className="col-span-12 overflow-hidden">
          <div className="px-8 py-6 border-b border-white/10 flex items-center justify-between bg-white/5">
            <h2 className="font-headline-md text-headline-md text-on-surface">
              Estimation Engine Workspace
            </h2>
            <div className="flex items-center gap-4">
              <span className="text-label-sm text-on-surface-variant">
                3 Gaps Identified
              </span>
              <button className="bg-white/5 hover:bg-white/10 text-on-surface px-4 py-2 rounded-lg font-label-md text-label-md border border-white/10 transition-all">
                Bulk Apply AI
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[720px]">
              <thead>
                <tr className="text-on-surface-variant font-label-sm text-label-sm border-b border-white/10">
                  <th className="px-8 py-4 font-medium uppercase tracking-wider">
                    Gap ID
                  </th>
                  <th className="px-8 py-4 font-medium uppercase tracking-wider">
                    Issue Description
                  </th>
                  <th className="px-8 py-4 font-medium uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-8 py-4 font-medium uppercase tracking-wider">
                    Est. Impact
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {GAPS.map((gap) => (
                  <tr
                    key={gap.id}
                    className="hover:bg-white/5 transition-colors"
                  >
                    <td className="px-8 py-6 font-label-md text-label-md text-primary">
                      {gap.id}
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex flex-col">
                        <span className="font-bold text-on-surface">
                          {gap.title}
                        </span>
                        <span className="text-body-sm text-on-surface-variant">
                          {gap.detail}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <span
                        className={`px-3 py-1 rounded-full text-[10px] font-black uppercase border ${STATUS_STYLES[gap.status]}`}
                      >
                        {gap.status}
                      </span>
                    </td>
                    <td className="px-8 py-6 text-on-surface font-body-md">
                      {gap.impact}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>

      {/* Floating action bar */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-30">
        <div className="glass-card px-8 py-4 rounded-2xl flex items-center gap-8 shadow-2xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-container/20 flex items-center justify-center">
              <span className="material-symbols-outlined text-primary-container">
                check_circle
              </span>
            </div>
            <div>
              <p className="text-label-sm font-bold text-on-surface">
                Ready to Finalize
              </p>
              <p className="text-[10px] text-on-surface-variant">
                3 AI Estimations applied
              </p>
            </div>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <button className="flex items-center gap-2 bg-primary-container text-on-primary-container px-8 py-3 rounded-xl font-label-md text-label-md font-black hover:scale-[1.05] active:scale-95 transition-all uppercase tracking-wider">
            Commit to Ledger
          </button>
        </div>
      </div>
    </div>
  );
}
