import type { Metadata } from "next";
import Link from "next/link";
import { MarketingHeader } from "@/components/marketing/MarketingHeader";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Methodology",
  description: "The rigorous, multi-layered CarbonIQ verification standard.",
};

const STACK_LAYERS = [
  {
    layer: "01",
    title: "Ingestion",
    description:
      "Direct telemetry from IoT hardware, industrial smart meters, and edge computing units. Zero manual entry.",
    icon: "sensors",
    tag: "Hardware Provenance",
  },
  {
    layer: "02",
    title: "Analysis",
    description:
      'Proprietary AI models cross-reference satellite flux data with local consumption to eliminate "leakage" or double-counting.',
    icon: "psychology",
    tag: "Neural Inference",
  },
  {
    layer: "03",
    title: "Validation",
    description:
      "Distributed Validator Nodes reach consensus on data validity. Outliers are rejected before ledger entry.",
    icon: "hub",
    tag: "BFT Consensus",
  },
  {
    layer: "04",
    title: "Finality",
    description:
      "Data is hashed and anchored into the CarbonIQ mainnet. Fully immutable, searchable, and auditable by anyone.",
    icon: "link",
    tag: "Ledger Anchor",
  },
];

const AI_POINTS = [
  {
    title: "Load Profile Inference",
    description:
      "Deconstructs composite utility signals to identify individual emission sources.",
  },
  {
    title: "Gap-Filling Logic",
    description:
      "Synthetic data generation for missing sensor intervals based on historical environmental flux.",
  },
  {
    title: "Confidence Indexing",
    description:
      "Every data point is tagged with an AI confidence score from 0.00 to 1.00.",
  },
];

const COMPLIANCE_ROWS = [
  {
    standard: "GHG Protocol",
    focus: "Global Accounting",
    alignment: "Full Scope 1, 2, and 3 traceability with tiered certainty levels.",
    status: "Active",
  },
  {
    standard: "Climate Active",
    focus: "Carbon Neutrality",
    alignment:
      "Inventory reporting compliant with public statement requirements.",
    status: "Active",
  },
  {
    standard: "ASRS",
    focus: "Sustainability Standards",
    alignment:
      "Automated assurance readiness for limited and reasonable assurance cycles.",
    status: "Active",
  },
  {
    standard: "SEC/CSRD",
    focus: "Climate Disclosure",
    alignment: "Machine-readable XBRL reporting format compatibility.",
    status: "In Roadmap",
  },
];

const RESOURCES = [
  {
    icon: "description",
    title: "Technical Whitepaper v2.4",
    description:
      "An 84-page document covering consensus algorithms and IoT hardware security.",
    cta: "Download PDF",
    ctaIcon: "download",
  },
  {
    icon: "code",
    title: "Verification SDK Guide",
    description:
      "How to integrate CarbonIQ nodes into your own industrial sensor network.",
    cta: "View Documentation",
    ctaIcon: "open_in_new",
    href: "/docs",
  },
  {
    icon: "shield",
    title: "Security Audit Report",
    description:
      "Latest audit by CertiK and Greenhouse Trust on smart contract integrity.",
    cta: "Download Report",
    ctaIcon: "verified_user",
  },
];

export default function MethodologyPage() {
  return (
    <>
      <MarketingHeader active="/methodology" />
      <main className="pt-16">
        {/* Hero */}
        <section className="pt-24 pb-32 px-margin-mobile md:px-margin-desktop container-max">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-gutter items-center">
            <div>
              <span className="font-label-md text-label-md text-primary-container tracking-widest uppercase mb-4 block">
                Engineered Integrity
              </span>
              <h1 className="font-headline-xl text-headline-xl mb-6 gradient-text">
                The CarbonIQ Standard
              </h1>
              <p className="font-body-lg text-body-lg text-on-surface-variant mb-8 max-w-xl">
                A rigorous, multi-layered &quot;Source of Truth&quot;
                framework. We eliminate carbon opacity by merging
                terrestrial IoT sensors, hyperspectral satellite imaging,
                and AI-driven load inference onto a high-throughput
                blockchain ledger.
              </p>
              <div className="flex gap-4">
                <Link
                  href="/docs"
                  className="px-8 py-4 bg-primary-container text-on-primary font-label-md text-label-md rounded-lg flex items-center gap-2 active:scale-95 transition-all"
                >
                  View API Docs{" "}
                  <span className="material-symbols-outlined">terminal</span>
                </Link>
                <button className="px-8 py-4 border border-outline text-on-surface font-label-md text-label-md rounded-lg hover:bg-white/5 transition-all active:scale-95">
                  Read Whitepaper
                </button>
              </div>
            </div>
            <GlassCard className="p-8 relative overflow-hidden">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 rounded-full bg-primary-container/20 flex items-center justify-center text-primary-container">
                  <span className="material-symbols-outlined">
                    satellite_alt
                  </span>
                </div>
                <div>
                  <div className="font-label-md text-label-md text-on-surface">
                    Data Fidelity
                  </div>
                  <div className="font-label-sm text-label-sm text-primary-container">
                    L0 Origin Established
                  </div>
                </div>
              </div>
              <div className="space-y-6">
                <div className="h-[2px] w-full bg-outline-variant relative">
                  <div className="absolute inset-y-0 left-0 bg-primary-container w-[92%] shadow-[0_0_8px_#00ff9d]" />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  {[
                    ["1.2ms", "Sync Latency"],
                    ["99.9%", "Node Uptime"],
                    ["256b", "Hash Depth"],
                  ].map(([value, label]) => (
                    <div key={label} className="text-center">
                      <div className="font-headline-md text-headline-md text-primary-container">
                        {value}
                      </div>
                      <div className="font-label-sm text-label-sm text-on-surface-variant">
                        {label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </GlassCard>
          </div>
        </section>

        {/* Verification stack */}
        <section className="py-24 px-margin-mobile md:px-margin-desktop bg-surface-container-lowest">
          <div className="container-max">
            <div className="text-center mb-16">
              <h2 className="font-headline-lg text-headline-lg mb-4">
                Verification Protocol Stack
              </h2>
              <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl mx-auto">
                Our four-layer validation architecture ensures that every
                metric reported is physically grounded and mathematically
                irrefutable.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">
              {STACK_LAYERS.map((item) => (
                <GlassCard
                  key={item.layer}
                  className="p-8 flex flex-col items-start h-full"
                >
                  <div className="font-label-sm text-label-sm text-primary-container mb-2">
                    LAYER {item.layer}
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-4">
                    {item.title}
                  </h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 flex-grow">
                    {item.description}
                  </p>
                  <div className="flex items-center gap-2 text-primary-container font-label-sm">
                    <span className="material-symbols-outlined text-[18px]">
                      {item.icon}
                    </span>
                    {item.tag}
                  </div>
                </GlassCard>
              ))}
            </div>
          </div>
        </section>

        {/* AI estimation */}
        <section className="py-32 px-margin-mobile md:px-margin-desktop container-max">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter items-center">
            <div className="lg:col-span-5">
              <h2 className="font-headline-lg text-headline-lg mb-6">
                High-Fidelity AI Estimation
              </h2>
              <p className="font-body-md text-body-md text-on-surface-variant mb-8">
                CarbonIQ&apos;s proprietary{" "}
                <span className="text-primary-container">FluxEngine™</span>{" "}
                achieves 95% accuracy in Scope 2 and 3 estimations by
                utilizing Non-Intrusive Load Monitoring (NILM).
              </p>
              <ul className="space-y-6">
                {AI_POINTS.map((point) => (
                  <li key={point.title} className="flex items-start gap-4">
                    <span className="material-symbols-outlined text-primary-container mt-1">
                      check_circle
                    </span>
                    <div>
                      <h4 className="font-label-md text-label-md text-on-surface">
                        {point.title}
                      </h4>
                      <p className="font-body-sm text-body-sm text-on-surface-variant">
                        {point.description}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="lg:col-span-7">
              <GlassCard className="p-1 overflow-hidden">
                <div className="bg-surface p-8 rounded-[11px]">
                  <div className="flex justify-between items-center mb-8">
                    <div className="font-label-md text-label-md">
                      Estimation vs. Real Metering
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2 text-label-sm font-label-sm">
                        <span className="w-3 h-3 rounded-full bg-primary-container" />{" "}
                        AI Predicted
                      </div>
                      <div className="flex items-center gap-2 text-label-sm font-label-sm">
                        <span className="w-3 h-3 rounded-full bg-outline" />{" "}
                        Actual Meter
                      </div>
                    </div>
                  </div>
                  <div className="h-64 flex items-end gap-2 px-4 border-b border-outline-variant">
                    {[60, 75, 90, 45, 65, 80, 70, 85, 95, 55, 40, 60].map(
                      (height, i) => (
                        <div
                          key={i}
                          className="flex-1 bg-primary-container/40 rounded-t-sm"
                          style={{ height: `${height}%` }}
                        />
                      ),
                    )}
                  </div>
                  <div className="flex justify-between pt-4 text-label-sm font-label-sm text-on-surface-variant">
                    <span>00:00</span>
                    <span>06:00</span>
                    <span>12:00</span>
                    <span>18:00</span>
                    <span>23:59</span>
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>
        </section>

        {/* Regulatory compliance */}
        <section className="py-24 px-margin-mobile md:px-margin-desktop bg-surface-container">
          <div className="container-max">
            <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12">
              <div>
                <h2 className="font-headline-lg text-headline-lg mb-4">
                  Regulatory Compliance
                </h2>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-xl">
                  Our methodology is pre-audited to meet the strictest
                  international carbon reporting requirements.
                </p>
              </div>
              <div className="flex items-center gap-3 bg-background/40 p-4 rounded-lg border border-outline-variant">
                <span className="material-symbols-outlined text-primary-container verified-badge-glow rounded-full">
                  verified
                </span>
                <span className="font-label-md text-label-md">
                  Audit Status: COMPLIANT
                </span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-outline-variant">
                    <th className="pb-6 font-label-md text-label-md text-on-surface-variant">
                      Standard
                    </th>
                    <th className="pb-6 font-label-md text-label-md text-on-surface-variant">
                      Focus Area
                    </th>
                    <th className="pb-6 font-label-md text-label-md text-on-surface-variant">
                      CarbonIQ Alignment
                    </th>
                    <th className="pb-6 font-label-md text-label-md text-on-surface-variant text-right">
                      Verification
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant">
                  {COMPLIANCE_ROWS.map((row) => (
                    <tr key={row.standard}>
                      <td className="py-6 font-headline-md text-headline-md">
                        {row.standard}
                      </td>
                      <td className="py-6 font-body-sm text-body-sm">
                        {row.focus}
                      </td>
                      <td className="py-6 font-body-sm text-body-sm">
                        {row.alignment}
                      </td>
                      <td className="py-6 text-right">
                        <span
                          className={`px-3 py-1 rounded-full text-label-sm font-label-sm ${
                            row.status === "Active"
                              ? "bg-primary-container/20 text-primary-container"
                              : "bg-secondary-container/20 text-secondary-container"
                          }`}
                        >
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Resource center */}
        <section className="py-32 px-margin-mobile md:px-margin-desktop container-max">
          <div className="text-center mb-16">
            <h2 className="font-headline-lg text-headline-lg mb-4">
              Resource Center
            </h2>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Deep dive into the math and engineering behind the platform.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            {RESOURCES.map((resource) => (
              <GlassCard
                key={resource.title}
                className="p-8 hover:-translate-y-1 transition-all group"
              >
                <span className="material-symbols-outlined text-[48px] text-primary-container mb-6 block">
                  {resource.icon}
                </span>
                <h4 className="font-headline-md text-headline-md mb-2">
                  {resource.title}
                </h4>
                <p className="font-body-sm text-body-sm text-on-surface-variant mb-6">
                  {resource.description}
                </p>
                <Link
                  href={resource.href ?? "#"}
                  className="flex items-center gap-2 text-primary-container font-label-md group-hover:gap-3 transition-all"
                >
                  {resource.cta}{" "}
                  <span className="material-symbols-outlined">
                    {resource.ctaIcon}
                  </span>
                </Link>
              </GlassCard>
            ))}
          </div>
        </section>
      </main>
      <MarketingFooter />
    </>
  );
}
