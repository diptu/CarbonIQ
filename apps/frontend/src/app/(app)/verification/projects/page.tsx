import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Project Verification Portal",
  description: "Submit evidence and track verification progress for a project.",
};

const STEPS = [
  { n: 1, label: "Data Ingestion", detail: "Completed Sep 12", state: "done" },
  { n: 2, label: "AI Validation", detail: "Completed Oct 05", state: "done" },
  { n: 3, label: "Peer Review", detail: "In Progress", state: "active" },
  { n: 4, label: "Final Issuance", detail: "Pending", state: "pending" },
];

const EVIDENCE = [
  { icon: "satellite_alt", iconColor: "text-primary-container", title: "Sentinel-2 Multi-Spectral", detail: "High-res vegetation index analysis of Sector A-14.", meta: "Uploaded: Oct 20, 2024", status: "Verified", statusClass: "bg-primary-container/10 text-primary-container border-primary-container/20" },
  { icon: "router", iconColor: "text-secondary-container", title: "IoT Soil Bio-Sensors", detail: "Real-time carbon sequestration telemetry from 40 nodes.", meta: "Live: 40/40 Online", status: "In Progress", statusClass: "bg-secondary-container/10 text-secondary-container border-secondary-container/20" },
  { icon: "description", iconColor: "text-error", title: "Local Land Certificates", detail: "Notarized documents for zone expansion area.", meta: "Action Required", status: "Flagged", statusClass: "bg-error/10 text-error border-error/20" },
  { icon: "biotech", iconColor: "text-primary-container", title: "Biomass Sampling Data", detail: "Field measurement report by Third-Party Auditor.", meta: "Auditor: Ecovision Labs", status: "Verified", statusClass: "bg-primary-container/10 text-primary-container border-primary-container/20" },
];

export default function VerificationProjectsPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto">
      <section className="mb-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8">
          <div>
            <h1 className="font-headline-xl text-headline-xl text-primary mb-2">
              Amazonia Reforestation
            </h1>
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-on-surface-variant font-label-md text-label-md bg-surface-container px-3 py-1 rounded">
                Project ID: AMZ-2024-081
              </span>
              <span className="flex items-center gap-1 text-primary-container font-label-md text-label-md">
                <span className="material-symbols-outlined text-[16px]">
                  verified
                </span>
                Verified Tier 1
              </span>
            </div>
          </div>
          <div className="mt-6 md:mt-0 text-right">
            <p className="font-label-md text-label-md text-on-surface-variant uppercase tracking-widest mb-1">
              Current Phase
            </p>
            <p className="font-headline-md text-headline-md text-primary-container">
              Peer Review
            </p>
          </div>
        </div>

        <div className="relative w-full h-1 bg-surface-container-highest rounded-full flex justify-between items-center mb-16 mt-12">
          <div
            className="absolute left-0 top-0 h-full bg-primary-container"
            style={{ width: "75%" }}
          />
          {STEPS.map((step) => (
            <div key={step.n} className="relative flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                  step.state === "done"
                    ? "bg-primary-container text-black shadow-[0_0_15px_rgba(0,255,157,0.6)]"
                    : step.state === "active"
                      ? "bg-primary-container text-black shadow-[0_0_15px_rgba(0,255,157,0.6)]"
                      : "bg-surface-container text-outline border border-outline-variant"
                }`}
              >
                {step.n}
              </div>
              <div className="absolute top-10 whitespace-nowrap text-center">
                <p
                  className={`font-label-md text-label-md ${
                    step.state === "pending"
                      ? "text-on-surface-variant"
                      : "text-primary"
                  }`}
                >
                  {step.label}
                </p>
                <p className="text-[10px] text-on-surface-variant">
                  {step.detail}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        <div className="md:col-span-8 flex flex-col gap-gutter">
          <GlassCard className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="font-headline-md text-headline-md text-primary">
                Evidence &amp; Logs
              </h2>
              <button className="text-primary-container hover:underline font-label-md text-label-md flex items-center gap-1">
                <span className="material-symbols-outlined">
                  upload_file
                </span>{" "}
                Upload Documentation
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {EVIDENCE.map((item) => (
                <div
                  key={item.title}
                  className="bg-surface-container-low border border-white/5 p-4 rounded-lg hover:border-primary-container/30 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded bg-surface-container-highest flex items-center justify-center">
                      <span
                        className={`material-symbols-outlined text-[32px] ${item.iconColor}`}
                      >
                        {item.icon}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase tracking-widest ${item.statusClass}`}
                    >
                      {item.status}
                    </span>
                  </div>
                  <h3 className="font-body-lg text-body-lg text-primary mb-1">
                    {item.title}
                  </h3>
                  <p className="text-body-sm text-on-surface-variant mb-3">
                    {item.detail}
                  </p>
                  <div className="flex justify-between items-center text-[12px] text-on-surface-variant">
                    <span>{item.meta}</span>
                    <span className="group-hover:text-primary-container transition-colors">
                      Details →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h2 className="font-headline-md text-headline-md text-primary mb-6">
              Auditor Review Panel
            </h2>
            <div className="space-y-6">
              <div className="bg-surface-container/50 border-l-4 border-primary-container p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-label-md text-label-md text-primary font-bold">
                    Dr. Helena Vance
                  </span>
                  <span className="text-body-sm text-on-surface-variant">
                    2 hours ago
                  </span>
                </div>
                <p className="text-body-md text-on-background">
                  Satellite imagery for Sector A-14 perfectly matches the
                  reported canopy growth metrics. AI validation discrepancy
                  of 0.4% is within acceptable variance for this ecosystem.
                </p>
              </div>
              <div className="bg-surface-container/30 p-4 rounded border border-white/5">
                <textarea
                  className="w-full bg-transparent border-none focus:ring-0 focus:outline-none text-on-background font-body-md min-h-[100px] placeholder:text-on-surface-variant/50"
                  placeholder="Add a comment or discrepancy report..."
                />
                <div className="flex justify-between items-center mt-4 pt-4 border-t border-white/5">
                  <div className="flex gap-2">
                    <span className="material-symbols-outlined text-[20px] text-on-surface-variant p-2 hover:bg-surface-container-highest rounded transition-colors cursor-pointer">
                      attach_file
                    </span>
                  </div>
                  <div className="flex gap-3">
                    <button className="px-4 py-2 text-on-surface-variant font-label-md text-label-md hover:text-primary transition-colors">
                      Save Draft
                    </button>
                    <button className="bg-white/10 hover:bg-white/20 text-primary px-6 py-2 rounded-lg font-label-md text-label-md transition-all">
                      Submit Review
                    </button>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4 p-6 border-2 border-dashed border-outline-variant rounded-xl group hover:border-primary-container/50 transition-all cursor-pointer">
                <div className="p-3 rounded-full bg-surface-container-highest group-hover:text-primary-container transition-colors">
                  <span className="material-symbols-outlined text-[32px]">
                    ink_pen
                  </span>
                </div>
                <div>
                  <h4 className="font-body-lg text-body-lg text-primary">
                    Request Digital Signature
                  </h4>
                  <p className="text-body-sm text-on-surface-variant">
                    Send final validation request to Lead Environmental
                    Auditor.
                  </p>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>

        <div className="md:col-span-4 flex flex-col gap-gutter">
          <GlassCard className="p-8 border-primary-container/40 neon-glow relative overflow-hidden">
            <h3 className="font-label-md text-label-md text-primary-container uppercase tracking-widest mb-6">
              Issuance Potential
            </h3>
            <div className="mb-8">
              <span className="font-headline-xl text-headline-xl text-primary leading-none">
                42,850
              </span>
              <span className="text-body-lg text-on-surface-variant ml-2 font-medium">
                Credits
              </span>
            </div>
            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center text-body-sm">
                <span className="text-on-surface-variant">
                  Pending Approval
                </span>
                <span className="text-primary">38,100</span>
              </div>
              <div className="flex justify-between items-center text-body-sm">
                <span className="text-on-surface-variant">In Dispute</span>
                <span className="text-error">4,750</span>
              </div>
              <div className="w-full h-1 bg-surface-container-highest rounded-full">
                <div
                  className="bg-primary-container h-full rounded-full"
                  style={{ width: "88%" }}
                />
              </div>
            </div>
            <button className="w-full bg-primary-container text-on-primary-container py-4 rounded-xl font-headline-md text-headline-md font-bold hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2">
              <span className="material-symbols-outlined">payments</span>
              Mint Credits
            </button>
            <p className="text-[11px] text-center text-on-surface-variant mt-4">
              Estimated completion date: Nov 15, 2024
            </p>
          </GlassCard>

          <GlassCard className="overflow-hidden h-64 relative flex items-center justify-center bg-gradient-to-br from-primary-container/10 to-surface-container">
            <span className="material-symbols-outlined text-[96px] text-primary-container/20">
              satellite_alt
            </span>
            <div className="absolute bottom-4 left-4">
              <p className="font-label-md text-label-md text-primary-container flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
                Live Satellite Monitoring
              </p>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
