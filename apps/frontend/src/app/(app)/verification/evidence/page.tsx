import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Evidence Timeline",
  description: "Full lifecycle audit trail for a carbon sequestration project.",
};

const STEPS = [
  {
    icon: "check_circle",
    title: "Data Submission",
    time: "Oct 24, 10:12 AM",
    status: "Completed",
    statusClass: "bg-primary/20 text-primary-fixed-dim",
    description:
      "Initial emissions data and offset documentation ingested via secure API. Payload size: 42.4MB. MD5 checksum verified.",
    state: "done",
  },
  {
    icon: "sync",
    title: "AI Validation",
    time: null,
    status: "In Progress",
    statusClass: "bg-secondary/20 text-secondary",
    description:
      "AI estimation engine is cross-referencing load profiles and filling data gaps with 96% confidence. Satellite imagery synthesis ongoing.",
    state: "active",
    progress: 85,
    stats: [
      ["Confidence Score", "96.2%"],
      ["Nodes Engaged", "14/16"],
    ],
  },
  {
    icon: "rule",
    title: "Protocol Verification",
    time: null,
    status: "Pending",
    statusClass: "bg-white/10 text-on-surface-variant",
    description:
      "Third-party auditor review and consensus validation. Expected to trigger upon AI completion.",
    state: "pending",
  },
  {
    icon: "token",
    title: "Smart Contract Minting",
    time: null,
    status: "Pending",
    statusClass: "bg-white/10 text-on-surface-variant",
    description:
      "Final credit issuance on the CarbonIQ ledger. Metadata will be permanently etched on-chain.",
    state: "pending",
  },
];

const DOCUMENTS = [
  { icon: "picture_as_pdf", iconClass: "bg-red-500/10 text-red-400", name: "Emissions_Inventory_Q3.pdf", meta: "12.4 MB • Oct 24" },
  { icon: "table_chart", iconClass: "bg-green-500/10 text-green-400", name: "Sensor_Logs_Raw.csv", meta: "8.2 MB • Oct 24" },
  { icon: "image", iconClass: "bg-blue-500/10 text-blue-400", name: "Site_Verification_Photo.jpg", meta: "2.1 MB • Oct 23" },
];

export default function VerificationEvidencePage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto">
      <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="bg-primary-container/10 text-primary-fixed-dim px-3 py-1 rounded-full text-xs font-bold border border-primary/20 tracking-wider uppercase">
              Project Active
            </span>
            <span className="text-on-surface-variant font-label-sm">
              Updated 2 minutes ago
            </span>
          </div>
          <h1 className="font-headline-xl text-headline-xl text-on-surface mb-2">
            Evidence Timeline
          </h1>
          <p className="text-on-surface-variant font-body-lg">
            Full lifecycle audit trail for CIQ-7724 Carbon Sequestration
            Initiative.
          </p>
        </div>
        <div className="grid grid-cols-2 md:flex items-center gap-4">
          <GlassCard className="px-6 py-4 min-w-[160px]">
            <p className="text-on-surface-variant text-[10px] uppercase font-bold tracking-[0.1em] mb-1">
              Project ID
            </p>
            <p className="text-on-surface font-headline-md text-headline-md">
              CIQ-7724
            </p>
          </GlassCard>
          <GlassCard className="px-6 py-4 min-w-[160px]">
            <p className="text-on-surface-variant text-[10px] uppercase font-bold tracking-[0.1em] mb-1">
              Status
            </p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary-container animate-pulse" />
              <p className="text-secondary font-headline-md text-headline-md">
                Validating
              </p>
            </div>
          </GlassCard>
          <GlassCard className="px-6 py-4 min-w-[160px] col-span-2">
            <p className="text-on-surface-variant text-[10px] uppercase font-bold tracking-[0.1em] mb-1">
              Est. Credits
            </p>
            <p className="text-primary font-headline-md text-headline-md">
              1,250{" "}
              <span className="text-sm font-label-md text-on-surface-variant">
                CRB
              </span>
            </p>
          </GlassCard>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        <section className="lg:col-span-8">
          <GlassCard className="rounded-[2rem] p-8 md:p-12">
            <div className="space-y-16">
              {STEPS.map((step) => (
                <div
                  key={step.title}
                  className={`flex gap-8 ${step.state === "pending" ? "opacity-40" : ""}`}
                >
                  <div className="flex flex-col items-center shrink-0">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center relative z-10 ${
                        step.state === "done"
                          ? "bg-primary-container text-on-primary-container neon-glow"
                          : step.state === "active"
                            ? "bg-surface-variant border-2 border-secondary-container text-secondary"
                            : "bg-surface-variant border-2 border-white/10 text-on-surface-variant"
                      }`}
                    >
                      <span className="material-symbols-outlined">
                        {step.icon}
                      </span>
                    </div>
                  </div>
                  <div className="pt-1 flex-1">
                    <div className="flex justify-between items-start mb-2 gap-4">
                      <h3 className="font-headline-md text-headline-md text-on-surface">
                        {step.title}
                      </h3>
                      {step.time && (
                        <span className="text-on-surface-variant font-label-sm bg-white/5 px-3 py-1 rounded-full shrink-0">
                          {step.time}
                        </span>
                      )}
                      {step.progress && (
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-secondary font-label-md">
                            {step.progress}%
                          </span>
                          <div className="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-secondary-container"
                              style={{ width: `${step.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mb-3">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-tighter ${step.statusClass}`}
                      >
                        {step.status}
                      </span>
                    </div>
                    <p className="text-on-surface-variant font-body-md leading-relaxed max-w-2xl">
                      {step.description}
                    </p>
                    {step.stats && (
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        {step.stats.map(([label, value]) => (
                          <div
                            key={label}
                            className="p-4 rounded-xl bg-white/5 border border-white/10"
                          >
                            <p className="text-[10px] text-on-surface-variant font-bold uppercase mb-2">
                              {label}
                            </p>
                            <span className="text-2xl font-bold text-on-surface">
                              {value}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </section>

        <aside className="lg:col-span-4 space-y-gutter">
          <GlassCard className="p-6">
            <h4 className="font-label-md text-on-surface mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-lg">
                link
              </span>
              Blockchain Hash
            </h4>
            <div className="bg-black/40 rounded-xl p-4 font-mono text-xs text-on-surface-variant break-all border border-white/5 hover:border-primary/30 transition-colors cursor-pointer">
              0x71C7656EC7ab88b098defB751B7401B5f6d8976Fbd3d74c2
              <span className="text-primary">...</span>5f6d8976F
            </div>
            <p className="mt-4 text-[10px] text-on-surface-variant italic">
              Permanently anchored to Ethereum Block #18,442,109
            </p>
          </GlassCard>

          <GlassCard className="p-6">
            <h4 className="font-label-md text-on-surface mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-lg">
                description
              </span>
              Proof Documents
            </h4>
            <div className="space-y-3">
              {DOCUMENTS.map((doc) => (
                <div
                  key={doc.name}
                  className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center ${doc.iconClass}`}
                    >
                      <span className="material-symbols-outlined">
                        {doc.icon}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-label-md text-on-surface">
                        {doc.name}
                      </p>
                      <p className="text-[10px] text-on-surface-variant">
                        {doc.meta}
                      </p>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors">
                    download
                  </span>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="overflow-hidden">
            <div className="h-40 relative flex items-center justify-center bg-gradient-to-br from-primary-container/10 to-surface-container">
              <span className="material-symbols-outlined text-[72px] text-primary-container/20">
                forest
              </span>
              <div className="absolute bottom-4 left-4">
                <p className="text-xs font-bold text-primary uppercase tracking-widest">
                  Satellite Validation
                </p>
                <p className="text-lg font-bold text-on-surface">
                  Area: Grid Sector 12-B
                </p>
              </div>
            </div>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-on-surface-variant text-xs">
                  Biomass Density
                </span>
                <span className="text-primary font-bold text-xs">
                  +12.4% vs baseline
                </span>
              </div>
              <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-container"
                  style={{ width: "72%" }}
                />
              </div>
            </div>
          </GlassCard>
        </aside>
      </div>
    </div>
  );
}
