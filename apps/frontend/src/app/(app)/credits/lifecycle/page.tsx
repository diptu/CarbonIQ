import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Credit Lifecycle Explorer",
  description: "Full provenance path for a carbon credit, from verification to retirement.",
};

const LIFECYCLE = [
  { icon: "check_circle", label: "Verification", date: "Aug 14, 2023", note: "Third-party audit confirmed biomass density via satellite.", color: "bg-primary-container text-on-primary-container" },
  { icon: "token", label: "Minting", date: "Sep 02, 2023", note: "Tokens issued on Polygon POS. ERC-1155 Standard.", color: "bg-secondary-container text-on-secondary-container" },
  { icon: "shopping_cart", label: "Sale", date: "Oct 12, 2023", note: "Purchased by Global Logistics Corp for ESG offset.", color: "bg-white text-surface" },
  { icon: "lock_person", label: "Retirement", date: "Nov 30, 2023", note: "Credits burned. Removed from circulation permanently.", color: "bg-[#00522f] text-primary-container border-2 border-primary-container" },
];

const BLOCK_DETAILS = [
  { label: "Transaction Hash", value: "0x71c...a3e49", mono: true },
  { label: "Block Height", value: "#48,291,012" },
];

const LEDGER_EVENTS = [
  { icon: "block", iconColor: "text-error", event: "Retirement", entity: "Global Logistics Corp", qty: "1,240 tCO2e", time: "2023-11-30 14:22:01" },
  { icon: "sync_alt", iconColor: "text-secondary", event: "Transfer", entity: "Marketplace v1.0", qty: "1,240 tCO2e", time: "2023-10-12 09:11:54" },
  { icon: "magic_button", iconColor: "text-primary-container", event: "Mint", entity: "CarbonIQ Protocol", qty: "1,240 tCO2e", time: "2023-09-02 18:45:33" },
];

export default function CreditLifecyclePage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto">
      <header className="mb-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-primary-container mb-2">
              <span className="material-symbols-outlined text-sm">
                verified
              </span>
              <span className="font-label-md uppercase tracking-tighter">
                Carbon Credit ID: CQ-9928-ALPHA
              </span>
            </div>
            <h1 className="font-headline-xl text-headline-xl text-primary leading-tight">
              Amazon Reforestation Provenance Path
            </h1>
          </div>
          <div className="flex gap-4">
            <div className="text-right">
              <p className="text-label-sm text-on-surface-variant">
                Current Status
              </p>
              <p className="text-headline-md text-primary font-bold">
                Retired
              </p>
            </div>
            <div className="w-px h-12 bg-white/10 mx-2" />
            <div className="text-right">
              <p className="text-label-sm text-on-surface-variant">
                Carbon Sequestration
              </p>
              <p className="text-headline-md text-primary font-bold">
                1,240 tCO2e
              </p>
            </div>
          </div>
        </div>
      </header>

      <section className="mb-16">
        <h2 className="font-headline-md text-headline-md text-primary mb-8 flex items-center gap-3">
          <span className="material-symbols-outlined">route</span> Lifecycle
          Explorer
        </h2>
        <GlassCard className="py-12 px-4 md:px-8 relative overflow-hidden">
          <div className="relative">
            <div className="absolute top-6 left-0 w-full h-[2px] bg-gradient-to-r from-primary-container via-secondary-container to-white/10 opacity-30" />
            <div className="flex justify-between items-start relative gap-2">
              {LIFECYCLE.map((step) => (
                <div
                  key={step.label}
                  className="flex flex-col items-center text-center w-1/4"
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center z-10 mb-4 border-4 border-surface ${step.color}`}
                  >
                    <span className="material-symbols-outlined">
                      {step.icon}
                    </span>
                  </div>
                  <h3 className="font-label-md text-primary-container mb-1 text-sm">
                    {step.label}
                  </h3>
                  <p className="text-label-sm text-on-surface-variant">
                    {step.date}
                  </p>
                  <p className="text-label-sm leading-snug mt-3 text-on-surface-variant hidden md:block">
                    {step.note}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        <section className="lg:col-span-8 flex flex-col">
          <h3 className="font-headline-md text-headline-md text-primary mb-6 flex items-center gap-3">
            <span className="material-symbols-outlined">public</span> Project
            Origin
          </h3>
          <GlassCard className="relative flex-grow overflow-hidden min-h-[320px] flex items-center justify-center bg-gradient-to-br from-primary-container/10 to-surface-container">
            <span className="material-symbols-outlined text-[140px] text-primary-container/10">
              public
            </span>
            <div className="absolute bottom-6 left-6 glass-card p-4 rounded-xl border-l-4 border-primary-container">
              <p className="text-label-sm uppercase tracking-widest text-on-surface-variant mb-1">
                Location Details
              </p>
              <p className="font-bold text-primary">Amazon Basin, Brazil</p>
              <p className="text-body-sm text-on-surface-variant">
                Coordinates: -3.4653, -62.2159
              </p>
            </div>
          </GlassCard>
        </section>

        <section className="lg:col-span-4">
          <h3 className="font-headline-md text-headline-md text-primary mb-6 flex items-center gap-3">
            <span className="material-symbols-outlined">database</span> Block
            Details
          </h3>
          <div className="flex flex-col gap-4">
            {BLOCK_DETAILS.map((detail) => (
              <GlassCard key={detail.label} className="p-6">
                <p className="text-label-sm text-on-surface-variant mb-2">
                  {detail.label}
                </p>
                <p
                  className={
                    detail.mono
                      ? "text-secondary font-mono text-sm break-all"
                      : "text-headline-md font-bold text-primary"
                  }
                >
                  {detail.value}
                </p>
              </GlassCard>
            ))}
            <GlassCard className="p-6 border-l-4 border-primary-container">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-label-sm text-on-surface-variant">
                    Proof of Sequestration
                  </p>
                  <p className="font-bold text-primary">
                    Verified Certificate
                  </p>
                </div>
                <span className="material-symbols-outlined text-primary-container">
                  verified
                </span>
              </div>
              <button className="flex items-center justify-center w-full bg-white/5 hover:bg-white/10 text-on-surface py-3 rounded-xl transition-all gap-2 border border-white/10">
                <span className="material-symbols-outlined text-sm">
                  open_in_new
                </span>
                <span className="text-label-md">View on IPFS</span>
              </button>
            </GlassCard>
          </div>
        </section>
      </div>

      <section className="mt-16">
        <div className="flex items-center justify-between mb-8">
          <h3 className="font-headline-md text-headline-md text-primary">
            Ledger Events
          </h3>
          <button className="text-primary-container text-label-md hover:underline">
            View All History
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left min-w-[640px]">
            <thead>
              <tr className="border-b border-white/10">
                <th className="pb-4 font-label-md text-on-surface-variant uppercase">
                  Event
                </th>
                <th className="pb-4 font-label-md text-on-surface-variant uppercase">
                  Entity
                </th>
                <th className="pb-4 font-label-md text-on-surface-variant uppercase">
                  Quantity
                </th>
                <th className="pb-4 font-label-md text-on-surface-variant uppercase">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {LEDGER_EVENTS.map((event) => (
                <tr
                  key={event.time}
                  className="hover:bg-white/5 transition-all"
                >
                  <td className="py-6 flex items-center gap-3">
                    <span
                      className={`material-symbols-outlined ${event.iconColor}`}
                    >
                      {event.icon}
                    </span>
                    <span className="font-bold">{event.event}</span>
                  </td>
                  <td className="py-6 text-on-surface-variant">
                    {event.entity}
                  </td>
                  <td className="py-6 text-primary">{event.qty}</td>
                  <td className="py-6 text-on-surface-variant">
                    {event.time}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
