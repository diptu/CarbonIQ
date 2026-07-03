import type { Metadata } from "next";
import Link from "next/link";
import { MarketingHeader } from "@/components/marketing/MarketingHeader";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "About",
  description: "Architecting the future of environmental trust.",
};

const VALUES = [
  {
    icon: "shield_lock",
    title: "Radical Transparency",
    description:
      "Every verification event is recorded on-chain, accessible to anyone, anywhere, forever.",
  },
  {
    icon: "neurology",
    title: "AI-Driven Precision",
    description:
      "Advanced machine learning models analyze multi-spectral satellite imagery to detect anomalies.",
  },
  {
    icon: "account_balance_wallet",
    title: "Decentralized Trust",
    description:
      "Distributed validator networks ensure no single entity can manipulate environmental data.",
  },
];

const STATS = [
  { label: "Founded", value: "2021" },
  { label: "Nodes Active", value: "120+" },
  { label: "Protocols Supported", value: "14" },
];

export default function AboutPage() {
  return (
    <>
      <MarketingHeader active="/about" />
      <main className="pt-16">
        {/* Hero */}
        <section className="relative flex items-center justify-center px-margin-mobile md:px-margin-desktop py-32 text-center">
          <div className="relative z-10 max-w-4xl">
            <span className="inline-block font-label-md text-label-md text-primary-fixed-dim tracking-[0.2em] mb-6">
              ESTABLISHING GLOBAL STANDARDS
            </span>
            <h1 className="font-headline-xl text-headline-xl gradient-text mb-8">
              Architecting the Future of Environmental Trust.
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto">
              CarbonIQ merges distributed ledger technology with
              satellite-grade AI to create the world&apos;s most robust
              verification infrastructure for the green economy.
            </p>
          </div>
        </section>

        {/* Mission / Vision */}
        <section className="py-24 px-margin-mobile md:px-margin-desktop container-max">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
            <GlassCard className="p-10">
              <div className="flex items-center gap-4 mb-6">
                <span className="material-symbols-outlined text-primary-container text-4xl">
                  target
                </span>
                <h2 className="font-headline-lg text-headline-lg">
                  Our Mission
                </h2>
              </div>
              <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">
                To decentralize environmental integrity by providing the
                world&apos;s most accurate and transparent carbon
                verification engine. We empower stakeholders with verifiable
                proof, eliminating greenwashing through code and climate
                science.
              </p>
            </GlassCard>
            <GlassCard className="p-10">
              <div className="flex items-center gap-4 mb-6">
                <span className="material-symbols-outlined text-secondary-container text-4xl">
                  visibility
                </span>
                <h2 className="font-headline-lg text-headline-lg">
                  Our Vision
                </h2>
              </div>
              <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">
                A global economy where every environmental claim is backed by
                immutable data and verified intelligence. We envision a
                future where climate action is as liquid and transparent as
                global finance.
              </p>
            </GlassCard>
          </div>
        </section>

        {/* Core values */}
        <section className="py-24 bg-surface-container-low px-margin-mobile md:px-margin-desktop">
          <div className="container-max">
            <div className="text-center mb-16">
              <h2 className="font-headline-lg text-headline-lg mb-4">
                Core Principles
              </h2>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Built on the foundation of scientific rigor and cryptographic
                truth.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
              {VALUES.map((value) => (
                <div
                  key={value.title}
                  className="flex flex-col items-center text-center p-8"
                >
                  <div className="w-16 h-16 rounded-2xl bg-primary-container/10 flex items-center justify-center mb-6 border border-primary-container/20">
                    <span className="material-symbols-outlined text-primary-container text-3xl">
                      {value.icon}
                    </span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-3">
                    {value.title}
                  </h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant">
                    {value.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Story */}
        <section className="py-32 px-margin-mobile md:px-margin-desktop container-max">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="relative">
              <div className="aspect-square rounded-3xl glass-card flex items-center justify-center">
                <span className="material-symbols-outlined text-[160px] text-primary-container/20">
                  forest
                </span>
              </div>
              <div className="absolute -bottom-10 -right-10 glass-card p-6 rounded-2xl hidden md:block">
                <div className="text-primary-container font-headline-md text-3xl mb-1">
                  50M+
                </div>
                <div className="font-label-md text-label-md uppercase tracking-wider text-on-surface-variant">
                  Tons Verified
                </div>
              </div>
            </div>
            <div>
              <h2 className="font-headline-lg text-headline-lg mb-8">
                Our Story
              </h2>
              <div className="space-y-6 font-body-lg text-body-lg text-on-surface-variant">
                <p>
                  Born at the intersection of climate science and
                  cryptographic innovation, CarbonIQ began with a single
                  question:{" "}
                  <span className="text-on-surface font-semibold italic">
                    How do we trust the invisible?
                  </span>
                </p>
                <p>
                  In 2021, our founders—a collective of remote sensing
                  engineers and decentralized finance architects—recognized a
                  fatal flaw in the voluntary carbon market: a profound lack
                  of real-time, immutable verification.
                </p>
                <p>
                  We built CarbonIQ to bridge this gap. By leveraging the
                  speed of AI to analyze ecological shifts and the permanence
                  of blockchain to store that intelligence, we&apos;ve
                  created a &quot;Source of Truth&quot; for the planet.
                </p>
              </div>
              <div className="mt-10 flex gap-12">
                {STATS.map((stat) => (
                  <div key={stat.label}>
                    <div className="text-on-surface font-headline-md text-headline-md">
                      {stat.value}
                    </div>
                    <div className="text-on-surface-variant font-label-sm text-label-sm">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-24 px-margin-mobile md:px-margin-desktop mb-12 container-max">
          <div className="glass-card rounded-[2rem] p-12 md:p-24 text-center">
            <h2 className="font-headline-xl text-headline-xl mb-6">
              Join the Verification Revolution
            </h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto mb-10">
              Ready to explore the most transparent ledger of environmental
              impact? Start tracking verified carbon offsets today.
            </p>
            <div className="flex flex-col md:flex-row gap-4 justify-center">
              <Link
                href="/signup"
                className="px-10 py-5 bg-primary-container text-on-primary font-extrabold rounded-full transition-all hover:scale-105 active:scale-95"
              >
                Enter Marketplace
              </Link>
              <Link
                href="/docs"
                className="px-10 py-5 bg-white/10 backdrop-blur-md text-on-surface font-bold rounded-full transition-all hover:bg-white/20 border border-white/10"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </section>
      </main>
      <MarketingFooter />
    </>
  );
}
