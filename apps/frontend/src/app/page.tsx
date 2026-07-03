import Link from "next/link";
import { MarketingHeader } from "@/components/marketing/MarketingHeader";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { GlassCard } from "@/components/ui";

const CAPABILITIES = [
  {
    icon: "psychology",
    title: "AI-Driven Ingestion",
    description:
      "Fill data gaps from utility bills and smart meters with temporal fusion transformers designed for emission prediction.",
  },
  {
    icon: "security",
    title: "Immutable Verification",
    description:
      "Lock every emission record and renewable attribution on a secure, audit-ready ledger with cryptographic proof of origin.",
  },
  {
    icon: "auto_awesome",
    title: "Automated Reporting",
    description:
      "Generate Climate Active and ASRS-aligned reports with one-click certification using our regulatory mapping engine.",
  },
];

const FEATURES = [
  "Real-time Grid Intensity Monitoring",
  "Supply Chain Attribution Mapping",
  "Multi-Standard Export Formats",
];

const TRUST_LOGOS = [
  "CLIMATE ACTIVE",
  "GHG PROTOCOL",
  "ASRS REGISTRY",
  "VERRA CONNECT",
  "GOLD STANDARD",
];

export default function LandingPage() {
  return (
    <>
      <MarketingHeader active="/" />
      <main className="pt-16 grid-bg">
        {/* Hero */}
        <section className="relative flex items-center px-margin-mobile md:px-margin-desktop py-32 overflow-hidden">
          <div className="container-max relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-container/10 border border-primary-container/20 text-primary-fixed-dim font-label-sm text-label-sm mb-6">
              <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
              Now LIVE: Enterprise Reporting v2.4
            </div>
            <h1 className="font-headline-xl text-headline-xl mb-6 gradient-text leading-[1.1]">
              The Standard for Decentralized Environmental Integrity
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant mb-10 max-w-xl">
              Verify, attribute, and report carbon emissions with{" "}
              <span className="text-primary-fixed-dim font-bold">
                ≥95% AI-driven accuracy
              </span>{" "}
              on an immutable ledger.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/signup"
                className="bg-primary-container text-on-primary-container px-8 py-4 rounded-lg font-bold font-label-md text-label-md flex items-center justify-center gap-2 hover:shadow-[0_0_20px_rgba(0,255,157,0.4)] transition-all"
              >
                Book an Enterprise Demo
                <span className="material-symbols-outlined text-[20px]">
                  arrow_forward
                </span>
              </Link>
              <Link
                href="/dashboard"
                className="bg-surface-variant border border-white/10 text-on-surface px-8 py-4 rounded-lg font-bold font-label-md text-label-md flex items-center justify-center gap-2 hover:bg-surface-bright transition-colors"
              >
                Launch Platform Explorer
              </Link>
            </div>
          </div>
        </section>

        {/* Social proof */}
        <section className="py-16 bg-surface-container-lowest border-y border-white/5 px-margin-mobile md:px-margin-desktop">
          <p className="text-center font-label-md text-label-md text-on-surface-variant uppercase tracking-widest mb-10">
            Trusted by leading climate-tech organizations
          </p>
          <div className="flex flex-wrap justify-center items-center gap-12 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
            {TRUST_LOGOS.map((logo) => (
              <div
                key={logo}
                className="font-headline-md font-bold tracking-tighter text-on-surface-variant"
              >
                {logo}
              </div>
            ))}
          </div>
        </section>

        {/* Capabilities */}
        <section className="py-32 px-margin-mobile md:px-margin-desktop">
          <div className="container-max">
            <div className="text-center max-w-2xl mx-auto mb-20">
              <h2 className="font-headline-lg text-headline-lg mb-4">
                Engineered for Radical Transparency
              </h2>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Our decentralized architecture ensures that every metric is
                verifiable, searchable, and impossible to duplicate.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
              {CAPABILITIES.map((cap) => (
                <GlassCard
                  key={cap.title}
                  className="p-8 group hover:-translate-y-2 transition-transform duration-300"
                >
                  <div className="w-12 h-12 rounded-lg bg-primary-container/10 flex items-center justify-center text-primary-fixed-dim mb-6 group-hover:bg-primary-container group-hover:text-on-primary-container transition-colors">
                    <span className="material-symbols-outlined">
                      {cap.icon}
                    </span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-4">
                    {cap.title}
                  </h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant">
                    {cap.description}
                  </p>
                </GlassCard>
              ))}
            </div>
          </div>
        </section>

        {/* Platform preview */}
        <section className="py-32 px-margin-mobile md:px-margin-desktop bg-surface-container">
          <div className="container-max">
            <div className="flex flex-col lg:flex-row gap-16 items-center">
              <div className="lg:w-1/2">
                <div className="inline-block px-3 py-1 rounded-full bg-secondary-container/10 border border-secondary-container/20 text-secondary-fixed-dim font-label-sm text-label-sm mb-6">
                  ANALYTICS ENGINE
                </div>
                <h2 className="font-headline-lg text-headline-lg mb-6">
                  High-Density Operational Intelligence
                </h2>
                <p className="font-body-md text-body-md text-on-surface-variant mb-8">
                  Experience a unified view of your environmental impact. Our
                  dashboard provides granular insights from scope 1 through
                  scope 3, with real-time anomaly detection and impact
                  forecasting.
                </p>
                <ul className="space-y-4 mb-10">
                  {FEATURES.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-center gap-3 font-body-sm text-body-sm"
                    >
                      <span className="material-symbols-outlined text-primary-fixed-dim">
                        check_circle
                      </span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="lg:w-1/2 relative">
                <div className="absolute -inset-4 bg-primary-container/10 blur-3xl rounded-full" />
                <GlassCard className="relative overflow-hidden p-8 shadow-2xl border-white/20 aspect-[4/3] flex items-center justify-center">
                  <span className="material-symbols-outlined text-[120px] text-primary-container/30">
                    monitoring
                  </span>
                  <div className="absolute bottom-8 right-8 glass-card p-4 flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary">
                      <span className="material-symbols-outlined">
                        verified
                      </span>
                    </div>
                    <div>
                      <p className="font-label-sm text-label-sm font-bold">
                        Audit Verified
                      </p>
                      <p className="text-[10px] opacity-60">
                        Verified via CarbonIQ-Node-42
                      </p>
                    </div>
                  </div>
                </GlassCard>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-32 px-margin-mobile md:px-margin-desktop text-center">
          <div className="container-max max-w-3xl mx-auto">
            <h2 className="font-headline-xl text-headline-xl mb-6">
              Ready to scale your carbon compliance?
            </h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant mb-12">
              Join hundreds of forward-thinking enterprises using CarbonIQ to
              build a verifiable future.
            </p>
            <Link
              href="/signup"
              className="inline-block bg-primary-container text-on-primary-container px-12 py-5 rounded-lg font-bold font-headline-md text-headline-md hover:scale-105 active:scale-95 transition-all shadow-lg shadow-primary-container/20"
            >
              Get Started with CarbonIQ
            </Link>
            <p className="mt-8 font-label-sm text-label-sm text-on-surface-variant">
              No commitment required. Custom enterprise pricing available.
            </p>
          </div>
        </section>
      </main>
      <MarketingFooter />
    </>
  );
}
