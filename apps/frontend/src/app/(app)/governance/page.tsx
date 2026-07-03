import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Governance Portal",
  description: "Propose, debate, and vote on protocols that drive the CarbonIQ ecosystem.",
};

const OVERVIEW = [
  { label: "Total Staked CRB", value: "42.8M", delta: "+2.4%" },
  { label: "Active Voters", value: "12,402", note: "84% Participation Rate" },
  { label: "Treasury Balance", value: "$18.2M" },
];

const PROPOSALS = [
  {
    status: "Voting Active",
    statusClass: "bg-primary-container/20 text-primary-container border-primary-container/30",
    meta: "Ends in 2d 4h",
    title: "CIP-42: Ocean Sequestration Credit Standard",
    description:
      "Implement a new validation framework for kelp-based carbon removal projects within the CarbonIQ ecosystem to diversify credit supply.",
    for: { pct: 82, label: "14.2M vCRB", color: "bg-primary-container" },
    against: { pct: 18, label: "3.1M vCRB" },
  },
  {
    status: "Review Pending",
    statusClass: "bg-secondary-container/20 text-secondary-container border-secondary-container/30",
    meta: "Quorum Reached",
    title: "CIP-43: DAO Treasury Allocation for Q3 Grants",
    description:
      "Proposal to allocate 1.5M USDC for the Q3 Ecosystem Growth program focusing on open-source auditing tools.",
    for: { pct: 96, label: "28.9M vCRB", color: "bg-secondary-container" },
    against: { pct: 4, label: "1.2M vCRB" },
  },
];

const TREASURY_ACTIONS = [
  { icon: "payments", iconClass: "bg-primary/10 text-primary", title: "Ecosystem Grant #92", detail: "Receiver: SolarAudit Protocol", value: "-50,000 USDC", time: "2h ago", valueClass: "text-primary" },
  { icon: "trending_up", iconClass: "bg-secondary/10 text-secondary", title: "Lido Staking Yield", detail: "Treasury Strategy: Auto-Compound", value: "+1.24 ETH", time: "1d ago", valueClass: "text-primary-container" },
  { icon: "verified_user", iconClass: "bg-primary/10 text-primary", title: "Validator Rewards", detail: "Infrastructure Node #04", value: "+12,050 CRB", time: "3d ago", valueClass: "text-primary-container" },
];

export default function GovernancePage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto">
      <div className="mb-12">
        <h1 className="font-headline-xl text-headline-xl text-primary mb-2">
          Governance Portal
        </h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
          Shape the future of CarbonIQ. Propose, debate, and vote on
          protocols that drive environmental restoration and high-integrity
          carbon markets.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        <div className="md:col-span-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {OVERVIEW.map((item) => (
            <GlassCard key={item.label} className="p-6">
              <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-2">
                {item.label}
              </p>
              <div className="flex items-end gap-2">
                <span className="font-headline-md text-headline-md text-primary">
                  {item.value}
                </span>
                {item.delta && (
                  <span className="font-label-sm text-label-sm text-primary-container mb-1">
                    {item.delta}
                  </span>
                )}
              </div>
              {item.note && (
                <p className="font-body-sm text-body-sm text-on-surface-variant mt-4">
                  {item.note}
                </p>
              )}
            </GlassCard>
          ))}
        </div>

        <GlassCard className="md:col-span-4 p-6 border-primary-container/30 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-start mb-6">
              <p className="font-label-md text-label-md text-primary font-bold">
                Your Voting Power
              </p>
              <span className="material-symbols-outlined text-primary">
                verified
              </span>
            </div>
            <div className="text-center py-4">
              <span className="font-headline-xl text-headline-xl text-primary">
                124.5K
              </span>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Voting Credits (vCRB)
              </p>
            </div>
          </div>
          <button className="w-full py-3 bg-white/5 border border-white/10 rounded-lg font-label-md text-label-md text-primary hover:bg-white/10 transition-colors">
            Increase Stake
          </button>
        </GlassCard>

        <div className="md:col-span-12 mt-4">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-headline-md text-headline-md text-primary">
              Active Proposals
            </h2>
            <button className="flex items-center gap-2 font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors">
              View Archive{" "}
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
            {PROPOSALS.map((proposal) => (
              <GlassCard
                key={proposal.title}
                className="p-8 hover:border-primary-container/40 transition-all cursor-pointer"
              >
                <div className="flex justify-between items-start mb-4">
                  <span
                    className={`px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full border ${proposal.statusClass}`}
                  >
                    {proposal.status}
                  </span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant">
                    {proposal.meta}
                  </span>
                </div>
                <h3 className="font-headline-md text-headline-md text-primary mb-2">
                  {proposal.title}
                </h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 line-clamp-2">
                  {proposal.description}
                </p>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-label-sm font-label-sm mb-1">
                      <span className="text-primary">
                        For ({proposal.for.pct}%)
                      </span>
                      <span className="text-on-surface-variant">
                        {proposal.for.label}
                      </span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${proposal.for.color}`}
                        style={{ width: `${proposal.for.pct}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-label-sm font-label-sm mb-1">
                      <span className="text-on-surface-variant">
                        Against ({proposal.against.pct}%)
                      </span>
                      <span className="text-on-surface-variant">
                        {proposal.against.label}
                      </span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-outline-variant rounded-full"
                        style={{ width: `${proposal.against.pct}%` }}
                      />
                    </div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>

        <div className="md:col-span-12 mt-8">
          <h2 className="font-headline-md text-headline-md text-primary mb-6">
            Treasury Transparency
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            <GlassCard className="p-6 flex flex-col justify-between h-64">
              <div>
                <p className="font-label-sm text-label-sm text-on-surface-variant mb-1">
                  Total Assets
                </p>
                <h4 className="font-headline-lg text-headline-lg text-primary">
                  $18,240,900
                </h4>
              </div>
              <div className="space-y-2">
                {[
                  ["USDC", "65%", "bg-primary-container"],
                  ["ETH", "25%", "bg-secondary-container"],
                  ["CRB", "10%", "bg-outline"],
                ].map(([label, pct, color]) => (
                  <div
                    key={label}
                    className="flex justify-between items-center text-label-sm font-label-sm"
                  >
                    <span className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${color}`} />
                      {label}
                    </span>
                    <span>{pct}</span>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="md:col-span-2 overflow-hidden">
              <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
                <h4 className="font-label-md text-label-md text-primary">
                  Recent Treasury Actions
                </h4>
                <span className="text-[10px] text-on-surface-variant uppercase tracking-widest">
                  Last 30 Days
                </span>
              </div>
              <div className="divide-y divide-white/5">
                {TREASURY_ACTIONS.map((action) => (
                  <div
                    key={action.title}
                    className="px-6 py-4 flex items-center justify-between hover:bg-white/5 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${action.iconClass}`}>
                        <span className="material-symbols-outlined text-sm">
                          {action.icon}
                        </span>
                      </div>
                      <div>
                        <p className="font-label-md text-label-md text-primary">
                          {action.title}
                        </p>
                        <p className="font-body-sm text-body-sm text-on-surface-variant">
                          {action.detail}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className={`font-label-md text-label-md ${action.valueClass}`}
                      >
                        {action.value}
                      </p>
                      <p className="font-body-sm text-body-sm text-on-surface-variant">
                        {action.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
