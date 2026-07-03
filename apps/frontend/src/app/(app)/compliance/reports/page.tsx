import type { Metadata } from "next";
import { GlassCard } from "@/components/ui";

export const metadata: Metadata = {
  title: "Compliance Reporting Center",
  description: "Automate enterprise environmental disclosures across global frameworks.",
};

const FRAMEWORKS = [
  { name: "GHG Protocol", meta: "Corporate Standard v3.1", active: true },
  { name: "SEC / CSRD", meta: "EU Disclosure Directives" },
  { name: "Climate Active", meta: "Australian Standards" },
  { name: "ASRS", meta: "Sustainability Reporting" },
];

const ALIGNMENT = [
  { scope: "Scope 1", pct: "100%", tag: "READY", badgeClass: "bg-primary-container/20 text-primary-container" },
  { scope: "Scope 2", pct: "92%", tag: "MISSING DATA", badgeClass: "bg-secondary-container/20 text-secondary-container" },
  { scope: "Scope 3", pct: "67%", tag: "ESTIMATED", badgeClass: "bg-tertiary-container/20 text-tertiary-container" },
];

const GAPS = [
  {
    icon: "warning",
    iconColor: "text-error",
    iconBg: "bg-error-container/20",
    title: "Missing Scope 2 Utility Data",
    detail:
      "Utility bills for the Q3 Tokyo regional office are missing 'Location-Based' emission factors. Upload raw CSV or connect via API.",
    cta: "Fix Now",
    impact: "+4.2% Score Impact",
  },
  {
    icon: "lightbulb",
    iconColor: "text-primary-container",
    iconBg: "bg-primary-container/20",
    title: "Optimization: Supply Chain Scope 3",
    detail:
      "42% of your Scope 3 emissions are currently based on industry averages. Inviting top 10 suppliers to CarbonIQ will replace estimates with real data.",
    cta: "Invite Suppliers",
  },
];

const READINESS = [
  { icon: "check_circle", title: "Data Gaps Filled", detail: "100% Scope 1 & 2 coverage identified.", done: true },
  { icon: "check_circle", title: "Renewables Matched", detail: "PPA certificates verified on-chain.", done: true },
  { icon: "pending", title: "Asset Inventory Verified", detail: "Validating 14 Scope 3 categories...", progress: 65 },
  { icon: "radio_button_unchecked", title: "Executive Signature", detail: "Pending final report generation.", pending: true },
];

const LEDGER = [
  { name: "Q1 Sustainability Ledger", generated: "Generated Mar 12, 2024", framework: "Climate Active", period: "Jan - Mar 2024", status: "Signed & Sealed", hash: "0x71C...4e92" },
  { name: "Annual Corporate Disclosure", generated: "Generated Feb 05, 2024", framework: "GHG Protocol", period: "FY 2023", status: "Archived", hash: "0x22F...9b11" },
  { name: "Mid-Market Resilience Test", generated: "Generated Dec 20, 2023", framework: "Internal Only", period: "Nov 2023", status: "Expired", hash: "0x4c2...de33" },
];

const STATUS_STYLES: Record<string, string> = {
  "Signed & Sealed": "bg-primary-container/10 text-primary-container border-primary-container/20",
  Archived: "bg-white/10 text-on-surface border-white/10",
  Expired: "bg-error-container/10 text-error border-error/20",
};

export default function ComplianceReportsPage() {
  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-gutter pb-20">
      <section>
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 bg-primary-container rounded-full animate-pulse" />
          <span className="font-label-md text-label-md text-primary-container tracking-widest uppercase">
            Audit Ready Environment
          </span>
        </div>
        <h1 className="font-headline-xl text-headline-xl mb-2">
          Compliance Reporting Center
        </h1>
        <p className="text-on-surface-variant max-w-2xl">
          Automate your enterprise environmental disclosures across global
          frameworks with audit-ready accuracy.
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        {/* Framework sidebar */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <h3 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-widest mb-2">
            Active Framework
          </h3>
          <div className="flex flex-col gap-3">
            {FRAMEWORKS.map((fw) => (
              <button
                key={fw.name}
                className={`glass-card p-4 rounded-xl flex items-center justify-between text-left transition-all ${
                  fw.active ? "border-primary-container neon-glow" : "hover:bg-surface-variant/50"
                }`}
              >
                <div>
                  <p className="font-bold text-primary font-headline-md text-headline-md">
                    {fw.name}
                  </p>
                  <p className="text-xs text-on-surface-variant mt-1">
                    {fw.meta}
                  </p>
                </div>
                {fw.active && (
                  <span className="material-symbols-outlined text-primary-container">
                    check_circle
                  </span>
                )}
              </button>
            ))}
          </div>
          <div className="mt-2 p-6 rounded-2xl bg-primary-container/5 border border-primary-container/20">
            <div className="flex items-center gap-2 mb-4">
              <span className="material-symbols-outlined text-primary-container">
                verified
              </span>
              <span className="font-label-md text-label-md font-bold text-primary-container">
                On-Chain Verified
              </span>
            </div>
            <p className="text-body-sm text-on-surface">
              Data integrity anchored on CarbonIQ Chain.
            </p>
            <div className="mt-4 h-1 w-full bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-primary-container w-[94%]" />
            </div>
            <p className="text-[10px] mt-2 text-on-surface-variant">
              94% of emissions data cryptographically signed.
            </p>
          </div>
        </div>

        {/* Main content */}
        <div className="lg:col-span-9 flex flex-col gap-gutter">
          {/* Alignment dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {ALIGNMENT.map((item) => (
              <GlassCard key={item.scope} className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <h4 className="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">
                    {item.scope}
                  </h4>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${item.badgeClass}`}
                  >
                    {item.tag}
                  </span>
                </div>
                <div className="flex items-end gap-3">
                  <span className="font-headline-xl text-headline-xl text-primary leading-none">
                    {item.pct}
                  </span>
                  <span className="text-on-surface-variant text-body-sm mb-1">
                    Aligned
                  </span>
                </div>
              </GlassCard>
            ))}
          </div>

          {/* Gaps & recommendations + readiness */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <GlassCard className="lg:col-span-3 p-8">
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center">
                  <span className="material-symbols-outlined text-surface font-bold">
                    auto_awesome
                  </span>
                </div>
                <div>
                  <h3 className="font-headline-md text-headline-md text-primary">
                    Compliance AI Analysis
                  </h3>
                  <p className="text-body-sm text-on-surface-variant">
                    Recommended actions to reach 100% alignment
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                {GAPS.map((gap) => (
                  <div
                    key={gap.title}
                    className="flex items-start gap-4 p-4 rounded-xl border border-white/5 hover:border-primary-container/30 transition-all bg-surface-container-low/50"
                  >
                    <div className={`${gap.iconBg} p-2 rounded-lg mt-1`}>
                      <span
                        className={`material-symbols-outlined text-sm ${gap.iconColor}`}
                      >
                        {gap.icon}
                      </span>
                    </div>
                    <div className="flex-1">
                      <h5 className="font-bold text-on-surface">
                        {gap.title}
                      </h5>
                      <p className="text-body-sm text-on-surface-variant mt-1">
                        {gap.detail}
                      </p>
                      <div className="mt-3 flex items-center gap-3">
                        <button className="text-primary-container font-label-md text-label-md flex items-center gap-1 hover:underline">
                          {gap.cta}
                          <span className="material-symbols-outlined text-sm">
                            open_in_new
                          </span>
                        </button>
                        {gap.impact && (
                          <>
                            <span className="text-outline-variant">|</span>
                            <span className="text-[10px] text-on-surface-variant">
                              {gap.impact}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="lg:col-span-2 p-8 border-l-4 border-l-primary-container flex flex-col gap-6">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-primary-container">
                  verified_user
                </span>
                <h3 className="font-headline-md text-headline-md text-on-surface">
                  Readiness Validator
                </h3>
              </div>
              <div className="flex flex-col gap-4">
                {READINESS.map((item) => (
                  <div
                    key={item.title}
                    className={`p-4 bg-black/20 rounded-2xl border border-white/5 flex items-start gap-4 relative ${
                      item.pending ? "opacity-50" : ""
                    }`}
                  >
                    <span
                      className={`material-symbols-outlined text-xl ${
                        item.done
                          ? "text-primary-container"
                          : item.progress
                            ? "text-secondary-container animate-pulse"
                            : "text-on-surface-variant"
                      }`}
                    >
                      {item.icon}
                    </span>
                    <div>
                      <p className="font-body-md text-body-md text-on-surface font-semibold">
                        {item.title}
                      </p>
                      <p className="text-xs text-on-surface-variant">
                        {item.detail}
                      </p>
                    </div>
                    {item.progress && (
                      <div className="absolute right-4 top-4 w-12 h-1 rounded-full bg-white/10 overflow-hidden">
                        <div
                          className="h-full bg-secondary-container"
                          style={{ width: `${item.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
              <div className="mt-auto bg-surface-container-high p-4 rounded-2xl border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-on-surface-variant">
                    Overall Compliance Score
                  </span>
                  <span className="text-primary-container font-bold">
                    89%
                  </span>
                </div>
                <div className="w-full h-2 bg-black/40 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary-container to-secondary-container w-[89%]" />
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Historical ledger */}
          <GlassCard className="overflow-hidden">
            <div className="p-8 border-b border-white/5 flex items-center justify-between">
              <h3 className="font-headline-md text-headline-md">
                Historical Ledger Records
              </h3>
              <button className="text-primary font-label-md hover:underline flex items-center gap-1">
                Generate Full Audit Report
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[720px]">
                <thead className="border-b border-white/10 text-on-surface-variant text-xs uppercase tracking-widest font-label-md">
                  <tr>
                    <th className="px-8 py-4 font-normal">Report Identity</th>
                    <th className="px-8 py-4 font-normal">Framework</th>
                    <th className="px-8 py-4 font-normal">Period</th>
                    <th className="px-8 py-4 font-normal">Status</th>
                    <th className="px-8 py-4 font-normal">
                      Verification Hash
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {LEDGER.map((row) => (
                    <tr
                      key={row.name}
                      className="hover:bg-white/[0.02] transition-colors"
                    >
                      <td className="px-8 py-6">
                        <p className="text-on-surface font-semibold">
                          {row.name}
                        </p>
                        <p className="text-[10px] text-on-surface-variant">
                          {row.generated}
                        </p>
                      </td>
                      <td className="px-8 py-6 text-on-surface-variant">
                        {row.framework}
                      </td>
                      <td className="px-8 py-6 text-on-surface-variant">
                        {row.period}
                      </td>
                      <td className="px-8 py-6">
                        <span
                          className={`px-3 py-1 rounded-full text-[10px] border font-bold uppercase tracking-tighter ${STATUS_STYLES[row.status]}`}
                        >
                          {row.status}
                        </span>
                      </td>
                      <td className="px-8 py-6 font-mono text-[10px] text-on-surface-variant opacity-50">
                        {row.hash}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}
