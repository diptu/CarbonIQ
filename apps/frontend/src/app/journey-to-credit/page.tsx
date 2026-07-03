import type { Metadata } from "next";
import { MarketingHeader } from "@/components/marketing/MarketingHeader";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Journey to Credit",
  description: "From verifiable environmental data to a tradeable carbon credit.",
};

const STEPS = [
  {
    node: 1,
    action: {
      tag: "Your Action",
      icon: "upload_file",
      title: "Upload IoT & Bills",
      description:
        "Initialize the pipeline by securely uploading your facility's utility bills and connecting live IoT sensors. We support standards like Green Button and LoRaWAN gateways.",
    },
    system: {
      tag: "System: Intake",
      icon: "api",
      title: "API Intake & Normalization",
      description:
        "CarbonIQ's ingest engines normalize disparate data streams into standardized emission factors, removing noise and preparing data for high-fidelity auditing.",
    },
  },
  {
    node: 2,
    action: {
      tag: "Your Action",
      icon: "map",
      title: "Submit Project Area",
      description:
        "Define your project boundaries using GeoJSON or shapefiles. Our AI will cross-reference this with land registry data to prevent double-spending.",
    },
    system: {
      tag: "System: Analysis",
      icon: "satellite_alt",
      title: "Satellite Biomass Analysis",
      description:
        "Multi-spectral satellite data is analyzed via neural networks to confirm carbon sequestration claims against historical benchmarks and load profiling.",
    },
    reverse: true,
  },
  {
    node: 3,
    action: {
      tag: "Your Action",
      icon: "hourglass_empty",
      title: "Await Audit",
      description:
        "Monitor the live validation pool. Your project is reviewed by an incentivized network of third-party validators for mathematical and scientific rigor.",
    },
    system: {
      tag: "System: Consensus",
      icon: "hub",
      title: "Validator Consensus",
      description:
        "A decentralized Proof-of-Action protocol reaches 67% BFT consensus on your data veracity, locking the claim into the immutable ledger.",
    },
  },
];

const PIPELINE_STATS = [
  { value: "14d", label: "AVG. TIME TO MINT" },
  { value: "0.02%", label: "REJECTION RATE" },
];

export default function JourneyToCreditPage() {
  return (
    <>
      <MarketingHeader active="/journey-to-credit" />
      <main className="pt-32 pb-40 px-margin-mobile md:px-margin-desktop container-max">
        <section className="text-center mb-32">
          <span className="text-primary-container font-label-md text-label-md uppercase tracking-widest mb-4 inline-block px-4 py-1 rounded-full border border-primary-container/20 bg-primary-container/5">
            RWA Pipeline v2.4
          </span>
          <h1 className="font-headline-xl text-headline-xl mb-6 tracking-tighter">
            Journey to Credit:{" "}
            <span className="text-primary-container">
              From Data to Tradeable NFT
            </span>
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto">
            Discover the lifecycle of high-integrity carbon credits. Our
            automated pipeline transforms verifiable environmental data into
            institutional-grade digital assets.
          </p>
        </section>

        <div className="space-y-24">
          {STEPS.map((step) => (
            <div
              key={step.node}
              className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-24 relative"
            >
              <div
                className={`flex flex-col md:items-end md:text-right ${
                  step.reverse ? "md:order-2 md:items-start md:text-left" : ""
                }`}
              >
                <GlassCard className="p-8 max-w-md">
                  <div
                    className={`flex items-center gap-3 mb-4 text-primary-container ${
                      step.reverse ? "justify-start" : "md:justify-end"
                    }`}
                  >
                    <span className="font-label-md text-label-md uppercase font-bold tracking-wider">
                      {step.action.tag}
                    </span>
                    <span className="material-symbols-outlined">
                      {step.action.icon}
                    </span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-3">
                    {step.action.title}
                  </h3>
                  <p className="text-on-surface-variant font-body-sm text-body-sm leading-relaxed">
                    {step.action.description}
                  </p>
                </GlassCard>
              </div>
              <div
                className={`flex flex-col md:items-start md:text-left ${
                  step.reverse ? "md:order-1 md:items-end md:text-right" : ""
                }`}
              >
                <GlassCard className="p-8 max-w-md border-l-4 border-l-primary-container/40">
                  <div
                    className={`flex items-center gap-3 mb-4 text-secondary ${
                      step.reverse ? "md:justify-end" : ""
                    }`}
                  >
                    <span className="material-symbols-outlined">
                      {step.system.icon}
                    </span>
                    <span className="font-label-md text-label-md uppercase font-bold tracking-wider">
                      {step.system.tag}
                    </span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-3">
                    {step.system.title}
                  </h3>
                  <p className="text-on-surface-variant font-body-sm text-body-sm leading-relaxed">
                    {step.system.description}
                  </p>
                </GlassCard>
              </div>
            </div>
          ))}

          {/* Final step: NFT minting */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-24">
            <div className="md:order-1 flex flex-col md:items-end md:text-right">
              <GlassCard className="p-8 max-w-md border-r-4 border-r-primary-container/40 bg-surface-container-high/40">
                <div className="flex items-center md:justify-end gap-3 mb-4 text-secondary">
                  <span className="font-label-md text-label-md uppercase font-bold tracking-wider">
                    System: Finality
                  </span>
                  <span className="material-symbols-outlined">token</span>
                </div>
                <h3 className="font-headline-md text-headline-md mb-3">
                  Immutable Ledger Minting
                </h3>
                <p className="text-on-surface-variant font-body-sm text-body-sm leading-relaxed">
                  The verified data is wrapped into an ERC-1155 token. All
                  metadata, including sensor logs and satellite imagery
                  hashes, are permanently attached.
                </p>
              </GlassCard>
            </div>
            <div className="md:order-2 flex flex-col md:items-start md:text-left">
              <GlassCard className="p-8 max-w-md bg-primary-container/10 border-primary-container/40">
                <div className="flex items-center gap-3 mb-4 text-primary-container">
                  <span className="material-symbols-outlined">
                    currency_exchange
                  </span>
                  <span className="font-label-md text-label-md uppercase font-bold tracking-wider">
                    Result: Verified
                  </span>
                </div>
                <h3 className="font-headline-md text-headline-md mb-3">
                  Tradeable Asset Issued
                </h3>
                <p className="text-on-surface-variant font-body-sm text-body-sm leading-relaxed mb-6">
                  Congratulations. Your carbon credit is now liquid. Trade,
                  retire, or use it as collateral within the CarbonIQ
                  Marketplace ecosystem.
                </p>
                <div className="flex gap-4">
                  <button className="bg-primary-container text-on-primary-container px-4 py-2 rounded-lg font-label-md text-label-md font-bold hover:scale-105 transition-all">
                    View Asset
                  </button>
                  <button className="border border-white/10 text-on-surface px-4 py-2 rounded-lg font-label-md text-label-md hover:bg-white/5 transition-all">
                    Trade Now
                  </button>
                </div>
              </GlassCard>
            </div>
          </div>
        </div>

        <section className="mt-40">
          <GlassCard className="p-12 rounded-3xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 items-center">
              <div className="lg:col-span-1">
                <h2 className="font-headline-lg text-headline-lg mb-4">
                  Real-time Pipeline Efficiency
                </h2>
                <p className="text-on-surface-variant font-body-md text-body-md">
                  Our automated ingestion and satellite verification reduced
                  processing time from 18 months to 14 days.
                </p>
                <div className="mt-8 flex gap-8">
                  {PIPELINE_STATS.map((stat) => (
                    <div key={stat.label}>
                      <div className="text-primary-container font-headline-md text-headline-md">
                        {stat.value}
                      </div>
                      <div className="text-on-surface-variant font-label-sm text-label-sm">
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="lg:col-span-2 h-64 relative">
                <div className="w-full h-full flex items-end gap-2 px-4">
                  {[40, 60, 55, 85, 70, 95, 45].map((height, i) => (
                    <div
                      key={i}
                      className="bg-primary-container/50 w-full rounded-t-lg"
                      style={{ height: `${height}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </GlassCard>
        </section>
      </main>
      <MarketingFooter />
    </>
  );
}
