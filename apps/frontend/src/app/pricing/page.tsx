import type { Metadata } from "next";
import { MarketingHeader } from "@/components/marketing/MarketingHeader";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { GlassCard } from "@/components/ui";
import { PricingTiers } from "./PricingTiers";

export const metadata: Metadata = {
  title: "Subscription & Pricing",
  description:
    "Transparent carbon verification at blockchain speed. Select a plan that scales with your environmental impact.",
};

const COMPARISON_ROWS = [
  {
    feature: "API Limits",
    community: "100 calls/hr",
    professional: "10,000 calls/hr",
    enterprise: "Unlimited / Managed",
  },
  {
    feature: "Data Retention",
    community: "30 Days",
    professional: "2 Years",
    enterprise: "Immutable / Custom",
  },
  {
    feature: "Verification Speed",
    community: "Standard Queue",
    professional: "Priority Queue",
    enterprise: "Instant / Real-time Verify",
  },
  {
    feature: "Reporting Formats",
    community: "JSON, CSV",
    professional: "PDF, XML, Webhooks",
    enterprise: "Custom ETL Pipelines",
  },
  {
    feature: "DAO Voting Power",
    community: "None",
    professional: "Standard (1x)",
    enterprise: "Governance Plus (5x)",
  },
];

export default function PricingPage() {
  return (
    <>
      <MarketingHeader active="/pricing" />
      <main className="pt-32 pb-24 px-margin-mobile md:px-margin-desktop container-max grid-bg">
        <header className="text-center mb-16">
          <h1 className="font-headline-xl text-headline-xl text-primary mb-4">
            Precision Climate Ledger Access
          </h1>
          <p className="text-on-surface-variant font-body-lg text-body-lg max-w-2xl mx-auto mb-10">
            Transparent carbon verification at blockchain speed. Select a
            plan that scales with your environmental impact.
          </p>
        </header>

        <PricingTiers />

        <section className="mb-24">
          <h2 className="font-headline-lg text-headline-lg text-center text-primary mb-12">
            Detailed Capabilities
          </h2>
          <div className="glass-card rounded-2xl overflow-hidden overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[640px]">
              <thead>
                <tr className="bg-surface-container-high/50 border-b border-white/10">
                  <th className="p-6 font-label-md text-label-md text-on-surface-variant w-1/4">
                    Feature
                  </th>
                  <th className="p-6 font-label-md text-label-md text-primary">
                    Community
                  </th>
                  <th className="p-6 font-label-md text-label-md text-primary-container bg-primary/5">
                    Professional
                  </th>
                  <th className="p-6 font-label-md text-label-md text-primary">
                    Enterprise
                  </th>
                </tr>
              </thead>
              <tbody className="text-body-sm font-body-sm">
                {COMPARISON_ROWS.map((row) => (
                  <tr
                    key={row.feature}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <td className="p-6 text-on-surface-variant font-medium">
                      {row.feature}
                    </td>
                    <td className="p-6">{row.community}</td>
                    <td className="p-6 bg-primary/5">{row.professional}</td>
                    <td className="p-6">{row.enterprise}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <GlassCard className="relative aspect-video overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center p-12 text-center">
              <div className="space-y-4">
                <div className="w-16 h-16 rounded-full bg-primary-container/20 flex items-center justify-center mx-auto border border-primary/30">
                  <span className="material-symbols-outlined text-primary-container text-4xl">
                    verified_user
                  </span>
                </div>
                <h4 className="font-headline-md text-headline-md text-primary">
                  Audited on Ethereum
                </h4>
                <p className="text-on-surface-variant text-body-sm">
                  All verifications are committed to the public ledger for
                  ultimate accountability.
                </p>
              </div>
            </div>
          </GlassCard>
          <div className="space-y-8">
            <h2 className="font-headline-lg text-headline-lg text-primary">
              Enterprise-Grade Security
            </h2>
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="shrink-0 w-12 h-12 bg-surface-container-high rounded-xl flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary-container">
                    encrypted
                  </span>
                </div>
                <div>
                  <h5 className="font-bold text-primary mb-1">
                    End-to-End Encryption
                  </h5>
                  <p className="text-on-surface-variant text-body-sm">
                    Your proprietary site data is encrypted before it ever
                    reaches our validators.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="shrink-0 w-12 h-12 bg-surface-container-high rounded-xl flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary-container">
                    hub
                  </span>
                </div>
                <div>
                  <h5 className="font-bold text-primary mb-1">
                    Decentralized Oracle Network
                  </h5>
                  <p className="text-on-surface-variant text-body-sm">
                    Multi-node consensus ensures no single point of failure
                    or data manipulation.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <MarketingFooter />
    </>
  );
}
